from collections import Counter
from typing import Any

import numpy as np
from sklearn.decomposition import PCA


def build_issue_axes_layout(normalized_embeddings, opinions, config: dict[str, Any]):
    vectors = np.asarray(normalized_embeddings, dtype=float)
    n_samples = len(vectors)

    if n_samples == 0:
        return [], _default_issue_axes_metadata()

    if n_samples == 1:
        return [[0.0, 0.0]], _default_issue_axes_metadata()

    n_components = min(2, n_samples, vectors.shape[1])
    if n_components < 1:
        return [[0.0, 0.0] for _ in range(n_samples)], _default_issue_axes_metadata()

    reducer = PCA(n_components=n_components, random_state=config["random_state"])
    coordinates = reducer.fit_transform(vectors)

    if n_components == 1:
        coordinates = np.column_stack([coordinates[:, 0], np.zeros(n_samples)])

    coordinates = _standardize_coordinates(coordinates)
    explained_variance = reducer.explained_variance_ratio_.tolist()
    if len(explained_variance) == 1:
        explained_variance.append(0.0)

    metadata = {
        "mode": "issue_axes",
        "title": "쟁점 축 보기",
        "description": "PCA 2D 좌표를 사용해 의견의 주요 긴장 방향을 축으로 표시합니다.",
        "coordinateNote": "이 좌표는 쟁점 방향을 읽기 위한 PCA 표시 좌표이며, 유사도 계산에는 사용하지 않습니다.",
        "xAxis": _axis_metadata(
            coordinates,
            opinions,
            axis_index=0,
            axis_name="x",
            explained_variance_ratio=explained_variance[0],
            config=config,
        ),
        "yAxis": _axis_metadata(
            coordinates,
            opinions,
            axis_index=1,
            axis_name="y",
            explained_variance_ratio=explained_variance[1],
            config=config,
        ),
    }
    return coordinates.astype(float).tolist(), metadata


def _standardize_coordinates(coordinates):
    coordinate_array = np.asarray(coordinates, dtype=float)
    mean = coordinate_array.mean(axis=0)
    std = coordinate_array.std(axis=0)
    std[std == 0] = 1.0
    return (coordinate_array - mean) / std


def _axis_metadata(coordinates, opinions, axis_index: int, axis_name: str, explained_variance_ratio: float, config: dict[str, Any]):
    coordinate_array = np.asarray(coordinates, dtype=float)
    if len(coordinate_array) == 0:
        return _default_axis_metadata(axis_name, explained_variance_ratio)

    extreme_count = max(
        config["issue_axis_min_extreme_count"],
        int(len(coordinate_array) * config["issue_axis_extreme_ratio"]),
    )
    extreme_count = min(extreme_count, max(1, len(coordinate_array) // 2))

    ordered_indices = np.argsort(coordinate_array[:, axis_index])
    negative_indices = ordered_indices[:extreme_count]
    positive_indices = ordered_indices[-extreme_count:]

    negative_label = _group_label([opinions[index] for index in negative_indices], config)
    positive_label = _group_label([opinions[index] for index in positive_indices], config)

    if negative_label == positive_label:
        negative_label = f"{negative_label} 낮은 방향"
        positive_label = f"{positive_label} 높은 방향"

    return {
        "title": f"{negative_label} ↔ {positive_label}",
        "negativeLabel": negative_label,
        "positiveLabel": positive_label,
        "description": f"{axis_name.upper()}축은 PCA가 찾은 주요 의견 차이 방향입니다.",
        "explainedVarianceRatio": float(explained_variance_ratio),
    }


def _group_label(opinions, config: dict[str, Any]):
    categories = [opinion.get("category", "").strip() for opinion in opinions if opinion.get("category")]
    if categories:
        category, _ = Counter(categories).most_common(1)[0]
        return _truncate(category, config["issue_axis_label_max_length"])

    texts = [opinion.get("text", "").strip() for opinion in opinions if opinion.get("text")]
    if texts:
        return _truncate(texts[0], config["issue_axis_label_max_length"])

    return "의견 방향"


def _truncate(text: str, max_length: int):
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."


def _default_issue_axes_metadata():
    return {
        "mode": "issue_axes",
        "title": "쟁점 축 보기",
        "description": "충분한 의견이 있을 때 PCA 기반 쟁점 축을 표시합니다.",
        "coordinateNote": "이 좌표는 쟁점 방향을 읽기 위한 PCA 표시 좌표입니다.",
        "xAxis": _default_axis_metadata("x", 0.0),
        "yAxis": _default_axis_metadata("y", 0.0),
    }


def _default_axis_metadata(axis_name: str, explained_variance_ratio: float):
    return {
        "title": f"{axis_name.upper()} 쟁점 축",
        "negativeLabel": "음수 방향",
        "positiveLabel": "양수 방향",
        "description": f"{axis_name.upper()}축은 PCA 기반 표시 좌표입니다.",
        "explainedVarianceRatio": float(explained_variance_ratio),
    }
