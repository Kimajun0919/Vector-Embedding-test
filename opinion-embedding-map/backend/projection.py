import math
from typing import Any

import numpy as np
import umap

from config import OPINION_MAP_LAYOUT_CONFIG


def project_embeddings_umap(normalized_embeddings, config: dict[str, Any] | None = None) -> list[list[float]]:
    layout_config = {**OPINION_MAP_LAYOUT_CONFIG, **(config or {})}
    vectors = np.asarray(normalized_embeddings, dtype=float)
    n_samples = len(vectors)

    if n_samples == 0:
        return []

    if n_samples == 1:
        return [[0.0, 0.0]]

    if n_samples < 5:
        return _deterministic_small_layout(n_samples)

    n_neighbors = min(layout_config["umap_neighbors"], n_samples - 1)
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=layout_config["umap_min_dist"],
        spread=layout_config["umap_spread"],
        metric=layout_config["umap_metric"],
        random_state=layout_config["random_state"],
    )

    coordinates = reducer.fit_transform(vectors)
    return coordinates.astype(float).tolist()


def _deterministic_small_layout(n_samples: int) -> list[list[float]]:
    if n_samples == 2:
        return [[-1.0, 0.0], [1.0, 0.0]]

    radius = 1.0
    coordinates = []
    for index in range(n_samples):
        angle = (2.0 * math.pi * index) / n_samples
        coordinates.append([radius * math.cos(angle), radius * math.sin(angle)])

    return coordinates
