from typing import Any

import numpy as np
from sklearn.preprocessing import normalize

from clustering import (
    build_cluster_payloads,
    cluster_opinions_hdbscan,
    create_island_layout,
    exaggerate_cluster_spacing,
    reassign_noise_to_nearest_cluster,
)
from config import OPINION_MAP_LAYOUT_CONFIG
from projection import project_embeddings_umap
from similarity import find_top_k_similar


def analyze_opinion_embeddings(opinions, embeddings, config: dict[str, Any] | None = None):
    layout_config = {**OPINION_MAP_LAYOUT_CONFIG, **(config or {})}

    if not opinions:
        return _empty_response(layout_config)

    vectors = np.asarray(embeddings, dtype=float)
    if vectors.ndim != 2 or len(vectors) != len(opinions):
        raise ValueError("Embedding count and opinion count must match.")

    normalized_embeddings = normalize(vectors)

    similar_by_id = find_top_k_similar(opinions, normalized_embeddings, k=5)
    labels, probabilities = cluster_opinions_hdbscan(normalized_embeddings, layout_config)
    labels, probabilities, hdbscan_labels, assignment_methods = reassign_noise_to_nearest_cluster(
        normalized_embeddings,
        labels,
        probabilities,
        layout_config,
    )
    base_coordinates = project_embeddings_umap(normalized_embeddings, layout_config)

    final_coordinates = base_coordinates
    layout_mode = "umap"
    if layout_config["use_island_layout"]:
        final_coordinates = create_island_layout(
            base_coordinates,
            labels,
            layout_config,
        )
        layout_mode = "island"
    elif layout_config["use_cluster_spacing"]:
        final_coordinates = exaggerate_cluster_spacing(
            base_coordinates,
            labels,
            factor=layout_config["cluster_spacing_factor"],
            noise_label=layout_config["noise_cluster_id"],
        )
        layout_mode = "cluster_emphasized"

    cluster_by_id, clusters = build_cluster_payloads(
        opinions,
        normalized_embeddings,
        labels,
        probabilities,
        base_coordinates,
        final_coordinates,
        layout_config,
        original_labels=hdbscan_labels,
        assignment_methods=assignment_methods,
    )

    analyzed = []
    for opinion, base_point, final_point in zip(opinions, base_coordinates, final_coordinates):
        analyzed.append(
            {
                **opinion,
                "x": float(final_point[0]),
                "y": float(final_point[1]),
                "baseX": float(base_point[0]),
                "baseY": float(base_point[1]),
                **cluster_by_id[opinion["id"]],
                "similarOpinions": similar_by_id[opinion["id"]],
            }
        )

    return {
        "opinions": analyzed,
        "clusters": clusters,
        "layoutMode": layout_mode,
        "layoutConfig": _public_layout_config(layout_config),
    }


def _empty_response(config: dict[str, Any]):
    return {
        "opinions": [],
        "clusters": [],
        "layoutMode": _layout_mode(config),
        "layoutConfig": _public_layout_config(config),
    }


def _public_layout_config(config: dict[str, Any]):
    return {
        "clusteringMethod": config["clustering_method"],
        "usePcaForClustering": config["use_pca_for_clustering"],
        "useClusterSpacing": config["use_cluster_spacing"],
        "clusterSpacingFactor": config["cluster_spacing_factor"],
        "reassignNoiseToNearestCluster": config["reassign_noise_to_nearest_cluster"],
        "noiseReassignmentThreshold": config["noise_reassignment_threshold"],
        "islandAnchorGap": config["island_anchor_gap"],
        "islandClusterRadius": config["island_cluster_radius"],
        "islandNoiseRadius": config["island_noise_radius"],
        "umapNeighbors": config["umap_neighbors"],
        "umapMinDist": config["umap_min_dist"],
        "umapSpread": config["umap_spread"],
        "umapMetric": config["umap_metric"],
        "useIslandLayout": config["use_island_layout"],
        "xAxisTitle": config["x_axis_title"],
        "yAxisTitle": config["y_axis_title"],
        "xAxisDescription": config["x_axis_description"],
        "yAxisDescription": config["y_axis_description"],
        "coordinateNote": config["coordinate_note"],
        "legendTitle": config["legend_title"],
        "legendDescription": config["legend_description"],
    }


def _layout_mode(config: dict[str, Any]):
    if config["use_island_layout"]:
        return "island"
    if config["use_cluster_spacing"]:
        return "cluster_emphasized"
    return "umap"
