import { useEffect, useState } from "react";
import { analyzeOpinions, getSampleOpinions } from "./api/opinionApi";
import OpinionDetailPanel from "./components/OpinionDetailPanel";
import OpinionMap from "./components/OpinionMap";
import type { AnalyzedOpinion, Opinion } from "./types/opinion";

export default function App() {
  const [sampleOpinions, setSampleOpinions] = useState<Opinion[]>([]);
  const [analyzedOpinions, setAnalyzedOpinions] = useState<AnalyzedOpinion[]>([]);
  const [selectedOpinion, setSelectedOpinion] = useState<AnalyzedOpinion | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

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
      setAnalyzedOpinions(result);
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
          <p className="eyebrow">AI 기반 공공서비스 도입에 대한 시민 의견</p>
          <h1>시민 의견 임베딩 지도</h1>
        </div>
        <button className="analyze-button" onClick={handleAnalyze} disabled={loading}>
          {loading ? "분석 중..." : "의견 분석 실행"}
        </button>
      </header>

      <section className="description">
        <p>
          이 의견 지도는 의견 간 의미적 유사도를 기반으로 배치됩니다. x축과 y축 자체에는 고정된 의미가 없으며,
          가까운 점일수록 의미적으로 유사한 의견입니다.
        </p>
        <p>
          샘플 응답 {sampleOpinions.length}건을 LUXIA Cloud Vector Embedding API로 임베딩한 뒤 UMAP으로 시각화합니다.
          색상은 주관식, 객관식-단일, 객관식-복수 응답 유형을 나타냅니다.
        </p>
      </section>

      {error && <div className="error-box">{error}</div>}
      {loading && <div className="loading-box">LUXIA 임베딩 생성, cosine similarity 계산, UMAP 투영을 수행하고 있습니다.</div>}

      <main className="content-grid">
        {analyzedOpinions.length > 0 ? (
          <OpinionMap
            opinions={analyzedOpinions}
            selectedOpinionId={selectedOpinion?.id}
            onSelectOpinion={setSelectedOpinion}
          />
        ) : (
          <section className="map-panel placeholder">
            <p>분석을 실행하면 100개 시민 의견이 UMAP 좌표 위에 표시됩니다.</p>
          </section>
        )}
        <OpinionDetailPanel opinion={selectedOpinion} />
      </main>
    </div>
  );
}
