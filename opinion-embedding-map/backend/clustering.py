import numpy as np
from sklearn.cluster import KMeans


def build_embedding_clusters(opinions, embeddings, n_clusters: int = 6) -> dict[str, dict]:
    if not opinions:
        return {}

    vectors = np.asarray(embeddings, dtype=float)
    cluster_count = min(n_clusters, len(opinions))

    if cluster_count == 1:
        representative = _representative_payload(opinions[0])
        return {
            opinions[0]["id"]: {
                "clusterId": 0,
                "clusterLabel": f"군집 1 · {opinions[0]['id']}",
                "clusterRepresentative": representative,
            }
        }

    normalized = _normalize(vectors)
    kmeans = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    labels = kmeans.fit_predict(normalized)

    representatives: dict[int, dict] = {}
    for cluster_id in range(cluster_count):
        member_indices = np.where(labels == cluster_id)[0]
        centroid = kmeans.cluster_centers_[cluster_id]
        distances = np.linalg.norm(normalized[member_indices] - centroid, axis=1)
        representative_index = int(member_indices[int(np.argmin(distances))])
        representatives[cluster_id] = _representative_payload(opinions[representative_index])

    result: dict[str, dict] = {}
    for opinion, cluster_id in zip(opinions, labels):
        representative = representatives[int(cluster_id)]
        result[opinion["id"]] = {
            "clusterId": int(cluster_id),
            "clusterLabel": f"군집 {int(cluster_id) + 1} · {representative['id']}",
            "clusterRepresentative": representative,
        }

    return result


def _normalize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def _representative_payload(opinion):
    return {
        "id": opinion["id"],
        "text": opinion["text"],
        "responseType": opinion["responseType"],
        "category": opinion["category"],
    }
