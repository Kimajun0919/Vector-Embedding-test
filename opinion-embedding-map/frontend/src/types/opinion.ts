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

export interface AnalyzedOpinion extends Opinion {
  x: number;
  y: number;
  similarOpinions: SimilarOpinion[];
}
