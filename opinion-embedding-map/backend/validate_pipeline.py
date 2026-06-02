import numpy as np

from analysis_pipeline import analyze_opinion_embeddings
from clustering import (
    build_cluster_payloads,
    create_island_layout,
    exaggerate_cluster_spacing,
    reassign_noise_to_nearest_cluster,
)
from config import OPINION_MAP_LAYOUT_CONFIG


def main():
    _assert_empty_dataset()
    _assert_small_datasets()
    _assert_large_dataset()
    _assert_noise_payload()
    _assert_noise_reassignment()
    _assert_cluster_spacing()
    _assert_island_layout()
    print("Backend opinion map pipeline validation passed.")


def _opinions(count: int):
    return [
        {
            "id": f"opinion_{index + 1:03d}",
            "text": f"sample opinion text {index + 1}",
            "responseType": "sample",
            "category": f"category_{index % 4}",
        }
        for index in range(count)
    ]


def _embeddings(count: int, dimensions: int = 16):
    rng = np.random.default_rng(42)
    centers = np.eye(4, dimensions)
    vectors = []
    for index in range(count):
        center = centers[index % len(centers)]
        vectors.append(center + rng.normal(0.0, 0.02, dimensions))
    return np.asarray(vectors, dtype=float).tolist()


def _assert_empty_dataset():
    result = analyze_opinion_embeddings([], [])
    assert result["opinions"] == []
    assert result["clusters"] == []


def _assert_small_datasets():
    one = analyze_opinion_embeddings(_opinions(1), _embeddings(1))
    assert len(one["opinions"]) == 1
    assert one["opinions"][0]["x"] == 0.0
    assert one["opinions"][0]["clusterId"] == 0

    four = analyze_opinion_embeddings(_opinions(4), _embeddings(4))
    assert len(four["opinions"]) == 4
    assert len(four["clusters"]) == 1
    assert all("x" in opinion and "y" in opinion for opinion in four["opinions"])


def _assert_large_dataset():
    result = analyze_opinion_embeddings(_opinions(100), _embeddings(100))
    assert len(result["opinions"]) == 100
    assert result["clusters"]
    assert result["layoutMode"] == "island"
    assert all("clusterId" in opinion for opinion in result["opinions"])
    assert all("baseX" in opinion and "baseY" in opinion for opinion in result["opinions"])
    assert result["opinions"][0]["similarOpinions"]


def _assert_noise_payload():
    opinions = _opinions(5)
    vectors = np.asarray(_embeddings(5), dtype=float)
    labels = [0, -1, 0, -1, 1]
    probabilities = [0.95, 0.0, 0.9, 0.0, 1.0]
    coordinates = [[0.0, 0.0], [0.5, 0.1], [0.1, 0.0], [0.6, 0.1], [2.0, 0.0]]

    _, clusters = build_cluster_payloads(
        opinions,
        vectors,
        labels,
        probabilities,
        coordinates,
        coordinates,
        OPINION_MAP_LAYOUT_CONFIG,
    )

    noise_cluster = next(cluster for cluster in clusters if cluster["clusterId"] == -1)
    assert noise_cluster["isNoise"] is True
    assert noise_cluster["clusterName"] == OPINION_MAP_LAYOUT_CONFIG["noise_cluster_label"]


def _assert_noise_reassignment():
    vectors = np.asarray(
        [
            [1.0, 0.0, 0.0],
            [0.98, 0.02, 0.0],
            [0.97, 0.01, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    labels = [0, 0, -1, -1]
    probabilities = [1.0, 0.9, 0.0, 0.0]
    config = {**OPINION_MAP_LAYOUT_CONFIG, "noise_reassignment_threshold": 0.55}

    reassigned_labels, reassigned_probabilities, original_labels, methods = reassign_noise_to_nearest_cluster(
        vectors,
        labels,
        probabilities,
        config,
    )

    assert original_labels == labels
    assert reassigned_labels[2] == 0
    assert methods[2] == "nearest_centroid"
    assert reassigned_probabilities[2] > 0.55
    assert reassigned_labels[3] == -1


def _assert_cluster_spacing():
    coordinates = [[-1.0, 0.0], [-0.8, 0.0], [1.0, 0.0], [0.8, 0.0]]
    labels = [0, 0, 1, 1]
    adjusted = exaggerate_cluster_spacing(coordinates, labels, factor=1.7, noise_label=-1)
    assert adjusted != coordinates
    assert coordinates[0] == [-1.0, 0.0]
    assert adjusted[0][0] < coordinates[0][0]
    assert adjusted[2][0] > coordinates[2][0]


def _assert_island_layout():
    coordinates = [
        [-2.0, 0.0],
        [-1.8, 0.1],
        [0.0, 2.0],
        [0.1, 1.8],
        [3.0, 0.0],
        [-3.0, 0.5],
    ]
    labels = [0, 0, 1, 1, -1, -1]
    adjusted = np.asarray(create_island_layout(coordinates, labels, OPINION_MAP_LAYOUT_CONFIG), dtype=float)
    label_array = np.asarray(labels)

    centers = {
        label: adjusted[label_array == label].mean(axis=0)
        for label in sorted(set(labels))
    }
    assert np.linalg.norm(centers[0] - centers[1]) >= OPINION_MAP_LAYOUT_CONFIG["island_anchor_gap"] * 0.8
    assert np.linalg.norm(centers[-1] - centers[0]) >= OPINION_MAP_LAYOUT_CONFIG["island_anchor_gap"] * 0.8

    noise_points = adjusted[label_array == -1]
    noise_radius = np.linalg.norm(noise_points - noise_points.mean(axis=0), axis=1).max()
    assert noise_radius <= OPINION_MAP_LAYOUT_CONFIG["island_noise_radius"] + 1e-9


if __name__ == "__main__":
    main()
