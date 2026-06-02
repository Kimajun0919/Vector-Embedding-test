from collections import Counter
from typing import Any

import numpy as np
from sklearn.decomposition import PCA

try:
    import hdbscan as hdbscan_package
except ImportError:  # pragma: no cover - exercised only when the package cannot be installed locally.
    hdbscan_package = None

try:
    from sklearn.cluster import HDBSCAN as SklearnHDBSCAN
except ImportError:  # pragma: no cover - older scikit-learn versions do not provide this fallback.
    SklearnHDBSCAN = None


def reduce_for_clustering(normalized_embeddings, max_components=50, random_state=42):
    vectors = np.asarray(normalized_embeddings, dtype=float)
    if vectors.size == 0:
        return vectors

    n_samples, embedding_dim = vectors.shape
    if n_samples < 5:
        return vectors

    n_components = min(max_components, n_samples - 1, embedding_dim)
    if n_components < 2:
        return vectors

    reducer = PCA(n_components=n_components, random_state=random_state)
    return reducer.fit_transform(vectors)


def cluster_opinions_hdbscan(normalized_embeddings, config: dict[str, Any]):
    vectors = np.asarray(normalized_embeddings, dtype=float)
    n_samples = len(vectors)

    if n_samples == 0:
        return [], []

    if n_samples < 5:
        return [0 for _ in range(n_samples)], [1.0 for _ in range(n_samples)]

    clustering_input = vectors
    if config["use_pca_for_clustering"]:
        clustering_input = reduce_for_clustering(
            vectors,
            max_components=config["pca_components_max"],
            random_state=config["random_state"],
        )

    min_cluster_size = max(
        config["min_cluster_size_min"],
        int(n_samples * config["min_cluster_size_ratio"]),
    )
    min_cluster_size = min(min_cluster_size, n_samples)
    min_samples = min(config["min_samples"], min_cluster_size)

    labels, probabilities = _fit_hdbscan(
        clustering_input,
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
    )

    if _all_noise(labels, config["noise_cluster_id"]):
        if n_samples < 10:
            return [0 for _ in range(n_samples)], [1.0 for _ in range(n_samples)]

        retry_cluster_size = min(max(3, int(n_samples * 0.02)), n_samples)
        labels, probabilities = _fit_hdbscan(
            clustering_input,
            min_cluster_size=retry_cluster_size,
            min_samples=1,
        )

        if _all_noise(labels, config["noise_cluster_id"]):
            return [0 for _ in range(n_samples)], [1.0 for _ in range(n_samples)]

    return labels, probabilities


def exaggerate_cluster_spacing(coords, labels, factor=1.7, noise_label=-1):
    coordinate_array = np.asarray(coords, dtype=float)
    label_array = np.asarray(labels)

    if len(coordinate_array) == 0:
        return coordinate_array.tolist()

    if len(coordinate_array) != len(label_array):
        return coordinate_array.tolist()

    unique_labels = [label for label in sorted(set(label_array.tolist())) if label != noise_label]
    if len(unique_labels) <= 1:
        return coordinate_array.tolist()

    adjusted = coordinate_array.copy()
    global_center = coordinate_array.mean(axis=0)

    for label in unique_labels:
        member_mask = label_array == label
        if member_mask.sum() == 0:
            continue

        cluster_center = coordinate_array[member_mask].mean(axis=0)
        direction = cluster_center - global_center
        if np.linalg.norm(direction) == 0:
            continue

        shift = direction * (factor - 1.0)
        adjusted[member_mask] = coordinate_array[member_mask] + shift

    return adjusted.tolist()


def build_cluster_payloads(
    opinions,
    normalized_embeddings,
    labels,
    probabilities,
    base_coordinates,
    final_coordinates,
    config: dict[str, Any],
):
    if not opinions:
        return {}, []

    vectors = np.asarray(normalized_embeddings, dtype=float)
    label_array = np.asarray(labels, dtype=int)
    probability_values = _probability_list(probabilities, len(opinions))
    base_array = np.asarray(base_coordinates, dtype=float)
    final_array = np.asarray(final_coordinates, dtype=float)

    cluster_ids = sorted(set(label_array.tolist()), key=lambda cluster_id: (cluster_id == config["noise_cluster_id"], cluster_id))
    cluster_by_label: dict[int, dict[str, Any]] = {}
    opinion_cluster_by_id: dict[str, dict[str, Any]] = {}

    for cluster_id in cluster_ids:
        member_indices = np.where(label_array == cluster_id)[0]
        is_noise = cluster_id == config["noise_cluster_id"]
        member_opinions = [opinions[index] for index in member_indices]

        representative = None
        representative_opinions = [_representative_payload(opinion) for opinion in member_opinions[:3]]

        if not is_noise:
            ordered_indices = _representative_indices(vectors, member_indices)
            representative = _representative_payload(opinions[ordered_indices[0]])
            representative_opinions = [_representative_payload(opinions[index]) for index in ordered_indices[:3]]

        cluster_name = _cluster_name(
            representative,
            member_opinions,
            is_noise=is_noise,
            config=config,
        )

        cluster_payload = {
            "clusterId": int(cluster_id),
            "clusterName": cluster_name,
            "clusterLabel": cluster_name,
            "count": int(len(member_indices)),
            "summary": _cluster_summary(cluster_name, len(member_indices), is_noise, config),
            "representativeOpinions": representative_opinions,
            "centerX": float(final_array[member_indices, 0].mean()),
            "centerY": float(final_array[member_indices, 1].mean()),
            "baseCenterX": float(base_array[member_indices, 0].mean()),
            "baseCenterY": float(base_array[member_indices, 1].mean()),
            "isNoise": is_noise,
        }
        if representative is not None:
            cluster_payload["representativeOpinion"] = representative

        cluster_by_label[int(cluster_id)] = cluster_payload

    for index, opinion in enumerate(opinions):
        cluster_id = int(label_array[index])
        cluster_payload = cluster_by_label[cluster_id]
        is_noise = cluster_id == config["noise_cluster_id"]
        opinion_payload = {
            "clusterId": cluster_id,
            "clusterName": cluster_payload["clusterName"],
            "clusterLabel": cluster_payload["clusterLabel"],
            "clusterProbability": probability_values[index],
            "isNoise": is_noise,
        }
        if "representativeOpinion" in cluster_payload:
            opinion_payload["clusterRepresentative"] = cluster_payload["representativeOpinion"]

        opinion_cluster_by_id[opinion["id"]] = opinion_payload

    return opinion_cluster_by_id, list(cluster_by_label.values())


def _fit_hdbscan(clustering_input, min_cluster_size: int, min_samples: int):
    if hdbscan_package is not None:
        clusterer = hdbscan_package.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric="euclidean",
        )
    elif SklearnHDBSCAN is not None:
        clusterer = SklearnHDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric="euclidean",
        )
    else:
        n_samples = len(clustering_input)
        return [0 for _ in range(n_samples)], [1.0 for _ in range(n_samples)]

    labels = clusterer.fit_predict(clustering_input)
    probabilities = getattr(clusterer, "probabilities_", None)
    if probabilities is None:
        probabilities = [None for _ in range(len(labels))]
    else:
        probabilities = probabilities.tolist()

    return labels.tolist(), probabilities


def _all_noise(labels, noise_label: int) -> bool:
    return bool(labels) and all(label == noise_label for label in labels)


def _probability_list(probabilities, count: int):
    if probabilities is None:
        return [None for _ in range(count)]

    result = []
    for probability in list(probabilities)[:count]:
        if probability is None:
            result.append(None)
        else:
            result.append(float(probability))

    if len(result) < count:
        result.extend([None for _ in range(count - len(result))])

    return result


def _representative_indices(vectors, member_indices):
    if len(member_indices) == 1:
        return [int(member_indices[0])]

    cluster_vectors = vectors[member_indices]
    centroid = cluster_vectors.mean(axis=0)
    distances = np.linalg.norm(cluster_vectors - centroid, axis=1)
    ordered_local_indices = np.argsort(distances)
    return [int(member_indices[index]) for index in ordered_local_indices]


def _representative_payload(opinion):
    return {
        "id": opinion["id"],
        "text": opinion["text"],
        "responseType": opinion["responseType"],
        "category": opinion["category"],
    }


def _cluster_name(representative, member_opinions, is_noise: bool, config: dict[str, Any]) -> str:
    if is_noise:
        return config["noise_cluster_label"]

    if len(member_opinions) <= 1:
        return config["default_cluster_label"]

    dominant_category = _dominant_category(member_opinions)
    if dominant_category:
        return f"{dominant_category} 중심 의견"

    if representative is None:
        return config["default_cluster_label"]

    return create_cluster_label(representative["text"])


def _dominant_category(member_opinions):
    categories = [opinion.get("category", "") for opinion in member_opinions if opinion.get("category")]
    if not categories:
        return None

    category, count = Counter(categories).most_common(1)[0]
    if count / len(categories) >= 0.6:
        return category

    return None


def create_cluster_label(representative_text: str, max_length=32) -> str:
    text = representative_text.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."


def _cluster_summary(cluster_name: str, count: int, is_noise: bool, config: dict[str, Any]) -> str:
    if is_noise:
        return "특정 의견군에 명확히 속하지 않는 의견입니다."

    if cluster_name == config["default_cluster_label"]:
        return f"전체 의견 {count}건을 하나의 기본 군집으로 표시합니다."

    return f"{cluster_name} 관련 의견 {count}건이 모인 군집입니다."
