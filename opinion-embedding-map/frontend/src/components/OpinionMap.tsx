import Plot from "react-plotly.js";
import type { PlotMouseEvent } from "plotly.js";
import type { AnalyzedOpinion } from "../types/opinion";

interface OpinionMapProps {
  opinions: AnalyzedOpinion[];
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
  "#16a34a"
];

export default function OpinionMap({ opinions, selectedOpinionId, onSelectOpinion }: OpinionMapProps) {
  const handleClick = (event: PlotMouseEvent) => {
    const id = event.points[0]?.customdata as string | undefined;
    const selected = opinions.find((opinion) => opinion.id === id);
    if (selected) {
      onSelectOpinion(selected);
    }
  };

  return (
    <section className="map-panel">
      <Plot
        data={[
          {
            type: "scatter",
            mode: "markers",
            name: "임베딩 군집",
            x: opinions.map((opinion) => opinion.x),
            y: opinions.map((opinion) => opinion.y),
            text: opinions.map(
              (opinion) =>
                `${opinion.id}<br>${opinion.clusterLabel}<br>${opinion.responseType} / ${opinion.category}<br>${opinion.text}`
            ),
            customdata: opinions.map((opinion) => opinion.id),
            hovertemplate: "%{text}<extra></extra>",
            marker: {
              color: opinions.map((opinion) => clusterColors[opinion.clusterId % clusterColors.length]),
              size: opinions.map((opinion) => (opinion.id === selectedOpinionId ? 18 : 11)),
              opacity: 0.88,
              line: {
                color: opinions.map((opinion) => (opinion.id === selectedOpinionId ? "#111827" : "#ffffff")),
                width: opinions.map((opinion) => (opinion.id === selectedOpinionId ? 3 : 1))
              }
            }
          }
        ]}
        layout={{
          autosize: true,
          height: 620,
          margin: { l: 54, r: 22, t: 24, b: 54 },
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
    </section>
  );
}
