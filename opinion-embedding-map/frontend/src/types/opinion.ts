export type Stance = "찬성" | "반대" | "조건부" | "기타";

export interface Opinion {
  id: string;
  text: string;
  stance: Stance | string;
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
