import { useMemo, useState } from "react";
import Plot from "react-plotly.js";
import type { PlotMouseEvent } from "plotly.js";
import type {
  AnalyzedOpinion,
  AnalyzeOpinionsResponse,
  OpinionCluster,
  OpinionLayoutMetadata,
  OpinionMapLayouts
} from "../types/opinion";

interface OpinionMapProps {
  opinions: AnalyzedOpinion[];
  clusters: OpinionCluster[];
  layoutMode?: AnalyzeOpinionsResponse["layoutMode"];
  layoutConfig?: AnalyzeOpinionsResponse["layoutConfig"];
  layouts?: OpinionMapLayouts;
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

function coordinateFor(opinion: AnalyzedOpinion, mode: string): { x: number; y: number } {
  if (mode === "issue_axes") {
    return {
      x: opinion.issueX ?? opinion.baseX ?? opinion.x,
      y: opinion.issueY ?? opinion.baseY ?? opinion.y
    };
  }

  if (mode === "umap") {
    return {
      x: opinion.baseX ?? opinion.x,
      y: opinion.baseY ?? opinion.y
    };
  }

  return {
    x: opinion.islandX ?? opinion.x,
    y: opinion.islandY ?? opinion.y
  };
}

function formatProbability(value?: number | null): string {
  if (value === undefined || value === null) {
    return "없음";
  }

  return `${Math.round(value * 100)}%`;
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

function truncate(text: string, maxLength = 72): string {
  return text.length <= maxLength ? text : `${text.slice(0, maxLength).trim()}...`;
}

function modeLabel(mode: string): string {
  if (mode === "issue_axes") {
    return "쟁점 축";
  }

  if (mode === "umap") {
    return "UMAP";
  }

  if (mode === "cluster_emphasized") {
    return "군집 강조";
  }

  return "구역 분리";
}

function activeLayoutMetadata(mode: string, layouts?: OpinionMapLayouts): OpinionLayoutMetadata | undefined {
  if (mode === "issue_axes") {
    return layouts?.issueAxes;
  }

  return layouts?.island;
}

function fallbackDescription(
  mode: string,
  spacingFactor: number,
  islandAnchorGap?: number
): string {
  if (mode === "issue_axes") {
    return "쟁점 축 보기: PCA가 찾은 주요 의견 차이 방향을 x/y축으로 표시합니다.";
  }

  if (mode === "island") {
    return `구역 분리 보기: 각 군집과 미분류 의견을 별도 구역으로 나누어 배치했습니다. 구역 간격은 ${(
      islandAnchorGap ?? 6
    ).toFixed(1)}입니다.`;
  }

  if (mode === "cluster_emphasized") {
    return `군집 강조 보기: 군집 간 거리를 시각적 구분을 위해 ${spacingFactor.toFixed(1)}배 보정했습니다.`;
  }

  return "UMAP 기본 배치 보기";
}

function axisDescription(axis?: OpinionLayoutMetadata["xAxis"]): string {
  if (!axis) {
    return "";
  }

  const endpoints = axis.negativeLabel && axis.positiveLabel
    ? `${axis.negativeLabel} ↔ ${axis.positiveLabel}`
    : undefined;
  const variance = typeof axis.explainedVarianceRatio === "number"
    ? `설명 분산 ${(axis.explainedVarianceRatio * 100).toFixed(1)}%`
    : undefined;

  return [axis.description, endpoints, variance].filter(Boolean).join(" · ");
}

export default function OpinionMap({
  opinions,
  clusters,
  layoutMode,
  layoutConfig,
  layouts,
  selectedOpinionId,
  onSelectOpinion
}: OpinionMapProps) {
  const initialMode = layoutMode ?? layouts?.defaultMode ?? "island";
  const [activeMode, setActiveMode] = useState(initialMode);
  const spacingFactor = layoutConfig?.clusterSpacingFactor ?? 1.7;
  const islandAnchorGap = layoutConfig?.islandAnchorGap;
  const activeLayout = activeLayoutMetadata(activeMode, layouts);

  const displayPoints = useMemo(
    () => opinions.map((opinion) => ({ opinion, ...coordinateFor(opinion, activeMode) })),
    [opinions, activeMode]
  );

  const labelClusters = useMemo(() => {
    return clusters
      .map((cluster) => {
        const members = displayPoints.filter(({ opinion }) => opinion.clusterId === cluster.clusterId);
        if (!members.length) {
          return undefined;
        }

        const centerX = members.reduce((sum, item) => sum + item.x, 0) / members.length;
        const centerY = members.reduce((sum, item) => sum + item.y, 0) / members.length;
        return { ...cluster, centerX, centerY };
      })
      .filter((cluster): cluster is OpinionCluster => Boolean(cluster));
  }, [clusters, displayPoints]);

  const availableModes = layouts?.availableModes?.length
    ? layouts.availableModes
    : ["island", "issue_axes"];
  const xAxis = activeLayout?.xAxis;
  const yAxis = activeLayout?.yAxis;
  const xAxisTitle = xAxis?.title ?? layoutConfig?.xAxisTitle ?? "구역 X";
  const yAxisTitle = yAxis?.title ?? layoutConfig?.yAxisTitle ?? "구역 Y";
  const xAxisDescription = axisDescription(xAxis) || layoutConfig?.xAxisDescription || "좌우 위치는 표시 좌표입니다.";
  const yAxisDescription = axisDescription(yAxis) || layoutConfig?.yAxisDescription || "상하 위치는 표시 좌표입니다.";
  const coordinateNote = activeLayout?.coordinateNote ?? layoutConfig?.coordinateNote ?? "baseX/baseY는 UMAP 원본 좌표이고 x/y는 최종 표시 좌표입니다.";
  const legendTitle = activeLayout?.legendTitle ?? layoutConfig?.legendTitle ?? "군집 범례";
  const legendDescription = activeLayout?.legendDescription ?? layoutConfig?.legendDescription ?? "색상은 최종 군집을 의미하고 회색은 미분류 의견입니다.";

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
          <p>{activeLayout?.description ?? fallbackDescription(activeMode, spacingFactor, islandAnchorGap)}</p>
        </div>
        <div className="layout-toggle" role="group" aria-label="지도 보기 방식">
          {availableModes.map((mode) => (
            <button
              type="button"
              key={mode}
              className={activeMode === mode ? "active" : undefined}
              onClick={() => setActiveMode(mode)}
            >
              {modeLabel(mode)}
            </button>
          ))}
        </div>
      </div>

      <Plot
        data={[
          {
            type: "scatter",
            mode: "markers",
            name: "의견",
            x: displayPoints.map((point) => point.x),
            y: displayPoints.map((point) => point.y),
            text: displayPoints.map(
              ({ opinion }) =>
                [
                  `<b>${opinion.id}</b>`,
                  `군집: ${opinion.clusterLabel}`,
                  `군집 ID: ${opinion.clusterId}`,
                  opinion.hdbscanClusterId !== undefined ? `HDBSCAN 원라벨: ${opinion.hdbscanClusterId}` : "",
                  `배정 방식: ${assignmentLabel(opinion)}`,
                  `군집 확률: ${formatProbability(opinion.clusterProbability)}`,
                  `${opinion.responseType} / ${opinion.category}`,
                  truncate(opinion.text)
                ].filter(Boolean).join("<br>")
            ),
            customdata: displayPoints.map(({ opinion }) => opinion.id),
            hovertemplate: "%{text}<extra></extra>",
            marker: {
              color: displayPoints.map(({ opinion }) => colorForCluster(opinion.clusterId, opinion.isNoise)),
              size: displayPoints.map(({ opinion }) => (opinion.id === selectedOpinionId ? 18 : 11)),
              opacity: 0.9,
              line: {
                color: displayPoints.map(({ opinion }) => (opinion.id === selectedOpinionId ? "#111827" : "#ffffff")),
                width: displayPoints.map(({ opinion }) => (opinion.id === selectedOpinionId ? 3 : 1))
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
          xaxis: { title: { text: xAxisTitle }, zeroline: false, gridcolor: "#e5e7eb" },
          yaxis: { title: { text: yAxisTitle }, zeroline: false, gridcolor: "#e5e7eb" },
          showlegend: false,
          hoverlabel: { align: "left" }
        }}
        config={{ responsive: true, displayModeBar: true }}
        useResizeHandler
        className="plot"
        onClick={handleClick}
      />

      <div className="axis-guide">
        <div>
          <strong>{xAxisTitle}</strong>
          <p>{xAxisDescription}</p>
        </div>
        <div>
          <strong>{yAxisTitle}</strong>
          <p>{yAxisDescription}</p>
        </div>
        <div>
          <strong>좌표 기준</strong>
          <p>{coordinateNote}</p>
        </div>
      </div>

      {clusters.length > 0 && (
        <div className="cluster-legend">
          <h3>{legendTitle}</h3>
          <p className="cluster-legend-description">{legendDescription}</p>
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
