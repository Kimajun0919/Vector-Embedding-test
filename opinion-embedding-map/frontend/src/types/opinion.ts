export type ResponseType = string;

export interface Opinion {
  id: string;
  text: string;
  responseType: ResponseType;
  category: string;
}

export interface SimilarOpinion extends Opinion {
  similarity: number;
  interpretation?: string;
}

export interface AnalyzedOpinion extends Opinion {
  x: number;
  y: number;
  baseX?: number;
  baseY?: number;
  islandX?: number;
  islandY?: number;
  issueX?: number;
  issueY?: number;
  clusterId: number;
  hdbscanClusterId?: number;
  clusterName: string;
  clusterLabel: string;
  clusterProbability?: number | null;
  isNoise?: boolean;
  wasNoise?: boolean;
  clusterAssignmentMethod?: "hdbscan" | "nearest_centroid" | "noise" | string;
  clusterRepresentative?: Opinion;
  similarOpinions: SimilarOpinion[];
}

export interface OpinionCluster {
  clusterId: number;
  clusterName: string;
  clusterLabel: string;
  count: number;
  summary?: string;
  centerX: number;
  centerY: number;
  baseCenterX?: number;
  baseCenterY?: number;
  representativeOpinion?: Opinion;
  representativeOpinions?: Opinion[];
  isNoise?: boolean;
}

export interface AnalyzeOpinionsResponse {
  opinions: AnalyzedOpinion[];
  clusters: OpinionCluster[];
  layoutMode?: "island" | "issue_axes" | "cluster_emphasized" | "umap" | string;
  layoutConfig?: {
    clusteringMethod?: string;
    usePcaForClustering?: boolean;
    useClusterSpacing?: boolean;
    clusterSpacingFactor?: number;
    reassignNoiseToNearestCluster?: boolean;
    noiseReassignmentThreshold?: number;
    islandAnchorGap?: number;
    islandClusterRadius?: number;
    islandNoiseRadius?: number;
    umapNeighbors?: number;
    umapMinDist?: number;
    umapSpread?: number;
    umapMetric?: string;
    useIslandLayout?: boolean;
    xAxisTitle?: string;
    yAxisTitle?: string;
    xAxisDescription?: string;
    yAxisDescription?: string;
    coordinateNote?: string;
    legendTitle?: string;
    legendDescription?: string;
  };
  layouts?: OpinionMapLayouts;
}

export interface OpinionAxisMetadata {
  title: string;
  negativeLabel?: string;
  positiveLabel?: string;
  description?: string;
  explainedVarianceRatio?: number;
}

export interface OpinionLayoutMetadata {
  mode: string;
  title: string;
  description?: string;
  coordinateNote?: string;
  xAxis?: OpinionAxisMetadata;
  yAxis?: OpinionAxisMetadata;
  legendTitle?: string;
  legendDescription?: string;
}

export interface OpinionMapLayouts {
  defaultMode: "island" | "issue_axes" | "cluster_emphasized" | "umap" | string;
  availableModes: string[];
  island?: OpinionLayoutMetadata;
  issueAxes?: OpinionLayoutMetadata;
}
