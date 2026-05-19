export type ResponseType = "주관식" | "객관식-단일" | "객관식-복수";

export interface Opinion {
  id: string;
  text: string;
  responseType: ResponseType | string;
  category: string;
}

export interface SimilarOpinion extends Opinion {
  similarity: number;
  interpretation?: string;
}

export interface ClusterRepresentative extends Opinion {}

export interface AnalyzedOpinion extends Opinion {
  x: number;
  y: number;
  clusterId: number;
  clusterName: string;
  clusterLabel: string;
  clusterRepresentative: ClusterRepresentative;
  similarOpinions: SimilarOpinion[];
}
