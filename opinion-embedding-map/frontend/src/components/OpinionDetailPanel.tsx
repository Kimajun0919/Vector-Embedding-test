import type { AnalyzedOpinion } from "../types/opinion";

interface OpinionDetailPanelProps {
  opinion?: AnalyzedOpinion;
}

function formatSimilarity(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function formatProbability(value?: number | null): string {
  if (value === undefined || value === null) {
    return "없음";
  }

  return `${Math.round(value * 100)}%`;
}

function formatCoordinate(value?: number): string {
  if (value === undefined) {
    return "-";
  }

  return value.toFixed(2);
}

function assignmentLabel(opinion: AnalyzedOpinion): string {
  if (opinion.clusterAssignmentMethod === "nearest_centroid") {
    return "가까운 군집으로 흡수";
  }

  if (opinion.isNoise) {
    return "미분류";
  }

  return "HDBSCAN 군집";
}

export default function OpinionDetailPanel({ opinion }: OpinionDetailPanelProps) {
  if (!opinion) {
    return (
      <aside className="detail-panel empty">
        <p>지도에서 의견을 선택하면 군집, 대표 의견, Top 5 유사 의견을 확인할 수 있습니다.</p>
      </aside>
    );
  }

  return (
    <aside className="detail-panel">
      <div className="selected-opinion">
        <div className="meta-row">
          <strong>{opinion.id}</strong>
          <span>{opinion.responseType}</span>
          <span>{opinion.category}</span>
          <span>{opinion.clusterLabel}</span>
          {opinion.isNoise && <span>미분류</span>}
          {opinion.wasNoise && !opinion.isNoise && <span>노이즈 흡수</span>}
        </div>
        <p>{opinion.text}</p>
        <dl className="coordinate-grid">
          <div>
            <dt>최종 좌표</dt>
            <dd>
              {formatCoordinate(opinion.x)}, {formatCoordinate(opinion.y)}
            </dd>
          </div>
          <div>
            <dt>UMAP 원본</dt>
            <dd>
              {formatCoordinate(opinion.baseX)}, {formatCoordinate(opinion.baseY)}
            </dd>
          </div>
          <div>
            <dt>군집 확률</dt>
            <dd>{formatProbability(opinion.clusterProbability)}</dd>
          </div>
          <div>
            <dt>배정 방식</dt>
            <dd>{assignmentLabel(opinion)}</dd>
          </div>
        </dl>
      </div>

      <section className="representative-box">
        <h2>{opinion.clusterLabel}</h2>
        {opinion.clusterRepresentative ? (
          <>
            <div className="meta-row">
              <strong>{opinion.clusterRepresentative.id}</strong>
              <span>{opinion.clusterRepresentative.responseType}</span>
              <span>{opinion.clusterRepresentative.category}</span>
            </div>
            <p>{opinion.clusterRepresentative.text}</p>
          </>
        ) : (
          <p>이 의견은 HDBSCAN에서 명확한 군집 대표를 계산하지 않은 미분류 의견입니다.</p>
        )}
      </section>

      <h2>Top 5 유사 의견</h2>
      <div className="similar-list">
        {opinion.similarOpinions.map((similar) => (
          <article className="similar-item" key={similar.id}>
            <div className="meta-row">
              <strong>{similar.id}</strong>
              <span>{formatSimilarity(similar.similarity)}</span>
              <span>{similar.responseType}</span>
              <span>{similar.category}</span>
            </div>
            <p>{similar.text}</p>
          </article>
        ))}
      </div>
    </aside>
  );
}
