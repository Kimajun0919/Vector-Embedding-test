import type { AnalyzedOpinion } from "../types/opinion";

interface OpinionDetailPanelProps {
  opinion?: AnalyzedOpinion;
}

function formatSimilarity(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export default function OpinionDetailPanel({ opinion }: OpinionDetailPanelProps) {
  if (!opinion) {
    return (
      <aside className="detail-panel empty">
        <p>의견 지도에서 하나의 점을 선택하면 해당 의견과 유사한 의견을 확인할 수 있습니다.</p>
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
        </div>
        <p>{opinion.text}</p>
      </div>

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
