import { useEffect, useState } from "react";
import { analyzeOpinions, getSampleOpinions } from "./api/opinionApi";
import OpinionDetailPanel from "./components/OpinionDetailPanel";
import OpinionMap from "./components/OpinionMap";
import type { AnalyzedOpinion, AnalyzeOpinionsResponse, Opinion } from "./types/opinion";

export default function App() {
  const [sampleOpinions, setSampleOpinions] = useState<Opinion[]>([]);
  const [analysisResult, setAnalysisResult] = useState<AnalyzeOpinionsResponse>();
  const [selectedOpinion, setSelectedOpinion] = useState<AnalyzedOpinion | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const analyzedOpinions = analysisResult?.opinions ?? [];

  useEffect(() => {
    getSampleOpinions()
      .then(setSampleOpinions)
      .catch((err) => setError(err.message));
  }, []);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(undefined);
    setSelectedOpinion(undefined);

    try {
      const result = await analyzeOpinions();
      setAnalysisResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">AI 공공서비스 시민 의견 임베딩 지도</p>
          <h1>시민 의견 군집 지도</h1>
        </div>
        <button className="analyze-button" onClick={handleAnalyze} disabled={loading}>
          {loading ? "분석 중..." : "의견 분석 실행"}
        </button>
      </header>

      <section className="description">
        <p>
          샘플 의견 {sampleOpinions.length}건을 LUXIA 임베딩, cosine similarity, HDBSCAN 군집, UMAP 배치로 분석합니다.
        </p>
        <p>
          군집 강조 보기는 의미적으로 가까운 의견군을 한눈에 구분할 수 있도록 UMAP 좌표의 군집 간 거리를 시각적으로 보정합니다.
        </p>
      </section>

      {error && <div className="error-box">{error}</div>}
      {loading && <div className="loading-box">임베딩 생성, 유사도 계산, HDBSCAN 군집화, UMAP 배치를 실행하고 있습니다.</div>}

      <main className="content-grid">
        {analyzedOpinions.length > 0 ? (
          <OpinionMap
            opinions={analyzedOpinions}
            clusters={analysisResult?.clusters ?? []}
            layoutMode={analysisResult?.layoutMode}
            layoutConfig={analysisResult?.layoutConfig}
            selectedOpinionId={selectedOpinion?.id}
            onSelectOpinion={setSelectedOpinion}
          />
        ) : (
          <section className="map-panel placeholder">
            <p>분석을 실행하면 시민 의견이 군집 강조 2D 지도에 표시됩니다.</p>
          </section>
        )}
        <OpinionDetailPanel opinion={selectedOpinion} />
      </main>
    </div>
  );
}
