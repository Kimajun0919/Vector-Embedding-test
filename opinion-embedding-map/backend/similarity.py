import numpy as np


def cosine_similarity(vec_a, vec_b) -> float:
    a = np.asarray(vec_a, dtype=float)
    b = np.asarray(vec_b, dtype=float)
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def similarity_label(score: float) -> str:
    if score >= 0.90:
        return "nearly duplicate opinion"
    if score >= 0.82:
        return "strongly similar opinion"
    if score >= 0.75:
        return "related opinion"
    return "weak or unrelated opinion"


def build_similarity_matrix(embeddings) -> list[list[float]]:
    vectors = np.asarray(embeddings, dtype=float)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = vectors / norms
    matrix = normalized @ normalized.T
    return matrix.tolist()


def find_top_k_similar(opinions, embeddings, k: int = 5) -> dict[str, list[dict]]:
    matrix = build_similarity_matrix(embeddings)
    result: dict[str, list[dict]] = {}

    for i, opinion in enumerate(opinions):
        scored = []
        for j, candidate in enumerate(opinions):
            if i == j:
                continue
            score = float(matrix[i][j])
            scored.append({
                "id": candidate["id"],
                "text": candidate["text"],
                "responseType": candidate["responseType"],
                "category": candidate["category"],
                "similarity": score,
                "interpretation": similarity_label(score),
            })
        result[opinion["id"]] = sorted(scored, key=lambda item: item["similarity"], reverse=True)[:k]

    return result
