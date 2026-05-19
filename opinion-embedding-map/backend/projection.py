import numpy as np
import umap


def project_embeddings_umap(embeddings: list[list[float]]) -> list[dict]:
    if not embeddings:
        return []

    vectors = np.asarray(embeddings, dtype=float)
    if len(vectors) == 1:
        return [{"x": 0.0, "y": 0.0}]
    if len(vectors) == 2:
        return [{"x": -1.0, "y": 0.0}, {"x": 1.0, "y": 0.0}]

    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=min(10, max(2, len(vectors) - 1)),
        min_dist=0.1,
        metric="cosine",
        random_state=42,
    )
    coordinates = reducer.fit_transform(vectors)

    mean = coordinates.mean(axis=0)
    std = coordinates.std(axis=0)
    std[std == 0] = 1.0
    normalized = (coordinates - mean) / std

    # UMAP x/y values are projection coordinates only. The axes do not have fixed semantic meanings.
    return [{"x": float(x), "y": float(y)} for x, y in normalized]
