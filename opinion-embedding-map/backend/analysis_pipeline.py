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
from issue_axes import build_issue_axes_layout
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
    issue_axis_coordinates, issue_axes_metadata = build_issue_axes_layout(
        normalized_embeddings,
        opinions,
        layout_config,
    )

    island_coordinates = base_coordinates
    if layout_config["use_island_layout"]:
        island_coordinates = create_island_layout(
            base_coordinates,
            labels,
            layout_config,
        )
    elif layout_config["use_cluster_spacing"]:
        island_coordinates = exaggerate_cluster_spacing(
            base_coordinates,
            labels,
            factor=layout_config["cluster_spacing_factor"],
            noise_label=layout_config["noise_cluster_id"],
        )

    layout_mode = _layout_mode(layout_config)
    final_coordinates = _coordinates_for_layout(
        layout_mode,
        base_coordinates=base_coordinates,
        island_coordinates=island_coordinates,
        issue_axis_coordinates=issue_axis_coordinates,
    )

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
    for opinion, base_point, island_point, issue_axis_point, final_point in zip(
        opinions,
        base_coordinates,
        island_coordinates,
        issue_axis_coordinates,
        final_coordinates,
    ):
        analyzed.append(
            {
                **opinion,
                "x": float(final_point[0]),
                "y": float(final_point[1]),
                "baseX": float(base_point[0]),
                "baseY": float(base_point[1]),
                "islandX": float(island_point[0]),
                "islandY": float(island_point[1]),
                "issueX": float(issue_axis_point[0]),
                "issueY": float(issue_axis_point[1]),
                **cluster_by_id[opinion["id"]],
                "similarOpinions": similar_by_id[opinion["id"]],
            }
        )

    return {
        "opinions": analyzed,
        "clusters": clusters,
        "layoutMode": layout_mode,
        "layoutConfig": _public_layout_config(layout_config),
        "layouts": _public_layouts(layout_config, issue_axes_metadata),
    }


def _empty_response(config: dict[str, Any]):
    return {
        "opinions": [],
        "clusters": [],
        "layoutMode": _layout_mode(config),
        "layoutConfig": _public_layout_config(config),
        "layouts": _public_layouts(config, None),
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
        "defaultLayoutMode": config["default_layout_mode"],
        "enableIssueAxesLayout": config["enable_issue_axes_layout"],
        "issueAxisExtremeRatio": config["issue_axis_extreme_ratio"],
        "issueAxisMinExtremeCount": config["issue_axis_min_extreme_count"],
        "xAxisTitle": config["x_axis_title"],
        "yAxisTitle": config["y_axis_title"],
        "xAxisDescription": config["x_axis_description"],
        "yAxisDescription": config["y_axis_description"],
        "coordinateNote": config["coordinate_note"],
        "legendTitle": config["legend_title"],
        "legendDescription": config["legend_description"],
    }


def _public_layouts(config: dict[str, Any], issue_axes_metadata):
    issue_axes = issue_axes_metadata or {
        "mode": "issue_axes",
        "title": "쟁점 축 보기",
        "description": "충분한 의견이 있을 때 PCA 기반 쟁점 축을 표시합니다.",
        "coordinateNote": "이 좌표는 쟁점 방향을 읽기 위한 PCA 표시 좌표입니다.",
        "xAxis": {
            "title": "X 쟁점 축",
            "negativeLabel": "음수 방향",
            "positiveLabel": "양수 방향",
            "description": "X축은 PCA 기반 표시 좌표입니다.",
            "explainedVarianceRatio": 0.0,
        },
        "yAxis": {
            "title": "Y 쟁점 축",
            "negativeLabel": "음수 방향",
            "positiveLabel": "양수 방향",
            "description": "Y축은 PCA 기반 표시 좌표입니다.",
            "explainedVarianceRatio": 0.0,
        },
    }
    return {
        "defaultMode": _layout_mode(config),
        "availableModes": ["island", "issue_axes"] if config["enable_issue_axes_layout"] else ["island"],
        "island": {
            "mode": "island",
            "title": "구역 분리 보기",
            "description": "각 군집과 남은 미분류 의견을 별도 구역으로 분리해 표시합니다.",
            "coordinateNote": config["coordinate_note"],
            "xAxis": {
                "title": config["x_axis_title"],
                "description": config["x_axis_description"],
            },
            "yAxis": {
                "title": config["y_axis_title"],
                "description": config["y_axis_description"],
            },
            "legendTitle": config["legend_title"],
            "legendDescription": config["legend_description"],
        },
        "issueAxes": issue_axes,
    }


def _layout_mode(config: dict[str, Any]):
    requested_mode = config.get("default_layout_mode", "island")
    if requested_mode == "issue_axes" and config["enable_issue_axes_layout"]:
        return "issue_axes"
    if requested_mode == "umap":
        return "umap"
    if requested_mode == "cluster_emphasized":
        return "cluster_emphasized"
    if config["use_island_layout"]:
        return "island"
    if config["use_cluster_spacing"]:
        return "cluster_emphasized"
    return "umap"


def _coordinates_for_layout(layout_mode, base_coordinates, island_coordinates, issue_axis_coordinates):
    if layout_mode == "issue_axes":
        return issue_axis_coordinates
    if layout_mode == "umap":
        return base_coordinates
    return island_coordinates
