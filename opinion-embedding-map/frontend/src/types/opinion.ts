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
  clusterId: number;
  clusterName: string;
  clusterLabel: string;
  clusterProbability?: number | null;
  isNoise?: boolean;
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
  layoutMode?: "island" | "cluster_emphasized" | "umap" | string;
  layoutConfig?: {
    clusteringMethod?: string;
    usePcaForClustering?: boolean;
    useClusterSpacing?: boolean;
    clusterSpacingFactor?: number;
    islandAnchorGap?: number;
    islandClusterRadius?: number;
    islandNoiseRadius?: number;
    umapNeighbors?: number;
    umapMinDist?: number;
    umapSpread?: number;
    umapMetric?: string;
    useIslandLayout?: boolean;
  };
}
