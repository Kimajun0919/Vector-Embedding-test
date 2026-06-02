import type { AnalyzedOpinion, AnalyzeOpinionsResponse, Opinion } from "../types/opinion";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // Keep the status-based message if the response is not JSON.
    }
    throw new Error(message);
  }

  return response.json();
}

export async function getSampleOpinions(): Promise<Opinion[]> {
  const data = await request<{ opinions: Opinion[] }>("/api/sample-opinions");
  return data.opinions;
}

export async function analyzeOpinions(opinions?: Opinion[]): Promise<AnalyzeOpinionsResponse> {
  const body = opinions ? JSON.stringify({ opinions }) : JSON.stringify({});
  const data = await request<AnalyzeOpinionsResponse | AnalyzedOpinion[]>("/api/analyze-opinions", {
    method: "POST",
    body
  });

  if (Array.isArray(data)) {
    return { opinions: data, clusters: [] };
  }

  return {
    opinions: data.opinions ?? [],
    clusters: data.clusters ?? [],
    layoutMode: data.layoutMode,
    layoutConfig: data.layoutConfig
  };
}
