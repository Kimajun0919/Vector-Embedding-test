import Plot from "react-plotly.js";
import type { PlotMouseEvent } from "plotly.js";
import type { AnalyzedOpinion, AnalyzeOpinionsResponse, OpinionCluster } from "../types/opinion";

interface OpinionMapProps {
  opinions: AnalyzedOpinion[];
  clusters: OpinionCluster[];
  layoutMode?: AnalyzeOpinionsResponse["layoutMode"];
  layoutConfig?: AnalyzeOpinionsResponse["layoutConfig"];
  selectedOpinionId?: string;
  onSelectOpinion: (opinion: AnalyzedOpinion) => void;
}

const clusterColors = [
  "#2563eb",
  "#059669",
  "#7c3aed",
  "#ea580c",
  "#0891b2",
  "#be123c",
  "#4f46e5",
  "#16a34a",
  "#ca8a04",
  "#db2777"
];

const noiseColor = "#9ca3af";

function colorForCluster(clusterId: number, isNoise?: boolean): string {
  if (isNoise || clusterId < 0) {
    return noiseColor;
  }

  return clusterColors[Math.abs(clusterId) % clusterColors.length];
}

function formatProbability(value?: number | null): string {
  if (value === undefined || value === null) {
    return "없음";
  }

  return `${Math.round(value * 100)}%`;
}

function truncate(text: string, maxLength = 72): string {
  return text.length <= maxLength ? text : `${text.slice(0, maxLength).trim()}...`;
}

export default function OpinionMap({
  opinions,
  clusters,
  layoutMode,
  layoutConfig,
  selectedOpinionId,
  onSelectOpinion
}: OpinionMapProps) {
  const labelClusters = clusters.filter((cluster) => cluster.count > 0);
  const spacingFactor = layoutConfig?.clusterSpacingFactor ?? 1.7;

  const handleClick = (event: PlotMouseEvent) => {
    const point = event.points[0];
    const pointIndex = typeof point?.pointIndex === "number"
      ? point.pointIndex
      : typeof point?.pointNumber === "number"
        ? point.pointNumber
        : undefined;
    const id = point?.customdata as string | undefined;
    const selected = id
      ? opinions.find((opinion) => opinion.id === id)
      : pointIndex !== undefined
        ? opinions[pointIndex]
        : undefined;

    if (selected) {
      onSelectOpinion(selected);
    }
  };

  return (
    <section className="map-panel">
      <div className="map-header">
        <div>
          <h2>의견 임베딩 지도</h2>
          <p>
            {layoutMode === "cluster_emphasized"
              ? `군집 강조 보기: 군집 간 거리를 시각적 구분을 위해 ${spacingFactor.toFixed(1)}배 보정했습니다.`
              : "UMAP 기본 배치 보기"}
          </p>
        </div>
      </div>

      <Plot
        data={[
          {
            type: "scatter",
            mode: "markers",
            name: "의견",
            x: opinions.map((opinion) => opinion.x),
            y: opinions.map((opinion) => opinion.y),
            text: opinions.map(
              (opinion) =>
                [
                  `<b>${opinion.id}</b>`,
                  `군집: ${opinion.clusterLabel}`,
                  `군집 ID: ${opinion.clusterId}`,
                  `군집 확률: ${formatProbability(opinion.clusterProbability)}`,
                  `${opinion.responseType} / ${opinion.category}`,
                  truncate(opinion.text)
                ].join("<br>")
            ),
            customdata: opinions.map((opinion) => opinion.id),
            hovertemplate: "%{text}<extra></extra>",
            marker: {
              color: opinions.map((opinion) => colorForCluster(opinion.clusterId, opinion.isNoise)),
              size: opinions.map((opinion) => (opinion.id === selectedOpinionId ? 18 : 11)),
              opacity: 0.9,
              line: {
                color: opinions.map((opinion) => (opinion.id === selectedOpinionId ? "#111827" : "#ffffff")),
                width: opinions.map((opinion) => (opinion.id === selectedOpinionId ? 3 : 1))
              }
            }
          },
          {
            type: "scatter",
            mode: "text",
            name: "군집 라벨",
            x: labelClusters.map((cluster) => cluster.centerX),
            y: labelClusters.map((cluster) => cluster.centerY),
            text: labelClusters.map((cluster) => cluster.clusterLabel),
            textposition: "middle center",
            textfont: {
              color: "#111827",
              size: 12
            },
            hoverinfo: "skip",
            showlegend: false
          }
        ]}
        layout={{
          autosize: true,
          height: 560,
          clickmode: "event+select",
          margin: { l: 54, r: 22, t: 14, b: 54 },
          paper_bgcolor: "#ffffff",
          plot_bgcolor: "#f8fafc",
          xaxis: { title: { text: "UMAP X" }, zeroline: false, gridcolor: "#e5e7eb" },
          yaxis: { title: { text: "UMAP Y" }, zeroline: false, gridcolor: "#e5e7eb" },
          showlegend: false,
          hoverlabel: { align: "left" }
        }}
        config={{ responsive: true, displayModeBar: true }}
        useResizeHandler
        className="plot"
        onClick={handleClick}
      />

      {clusters.length > 0 && (
        <div className="cluster-legend">
          <h3>군집 요약</h3>
          <div className="cluster-legend-list">
            {clusters.map((cluster) => (
              <article className="cluster-legend-row" key={cluster.clusterId}>
                <span
                  className="cluster-swatch"
                  style={{ backgroundColor: colorForCluster(cluster.clusterId, cluster.isNoise) }}
                  aria-hidden="true"
                />
                <div>
                  <div className="cluster-legend-title">
                    <strong>{cluster.clusterLabel}</strong>
                    <span>{cluster.count}건</span>
                  </div>
                  {cluster.representativeOpinion && <p>{truncate(cluster.representativeOpinion.text, 96)}</p>}
                  {!cluster.representativeOpinion && cluster.summary && <p>{cluster.summary}</p>}
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
