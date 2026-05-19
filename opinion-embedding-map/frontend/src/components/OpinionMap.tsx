import Plot from "react-plotly.js";
import type { PlotMouseEvent } from "plotly.js";
import type { AnalyzedOpinion } from "../types/opinion";

interface OpinionMapProps {
  opinions: AnalyzedOpinion[];
  selectedOpinionId?: string;
  onSelectOpinion: (opinion: AnalyzedOpinion) => void;
}

const stanceColors: Record<string, string> = {
  "찬성": "#2563eb",
  "반대": "#dc2626",
  "조건부": "#059669",
  "기타": "#7c3aed"
};

export default function OpinionMap({ opinions, selectedOpinionId, onSelectOpinion }: OpinionMapProps) {
  const stances = ["찬성", "반대", "조건부", "기타"];

  const data = stances.map((stance) => {
    const group = opinions.filter((opinion) => opinion.stance === stance);
    return {
      type: "scattergl" as const,
      mode: "markers" as const,
      name: stance,
      x: group.map((opinion) => opinion.x),
      y: group.map((opinion) => opinion.y),
      text: group.map((opinion) => `${opinion.id}<br>${opinion.stance} / ${opinion.category}<br>${opinion.text}`),
      customdata: group.map((opinion) => opinion.id),
      hovertemplate: "%{text}<extra></extra>",
      marker: {
        color: stanceColors[stance],
        size: group.map((opinion) => opinion.id === selectedOpinionId ? 17 : 11),
        opacity: 0.86,
        line: {
          color: group.map((opinion) => opinion.id === selectedOpinionId ? "#111827" : "#ffffff"),
          width: group.map((opinion) => opinion.id === selectedOpinionId ? 3 : 1)
        }
      }
    };
  });

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
        data={data}
        layout={{
          autosize: true,
          height: 620,
          margin: { l: 54, r: 22, t: 24, b: 54 },
          paper_bgcolor: "#ffffff",
          plot_bgcolor: "#f8fafc",
          xaxis: { title: { text: "UMAP X" }, zeroline: false, gridcolor: "#e5e7eb" },
          yaxis: { title: { text: "UMAP Y" }, zeroline: false, gridcolor: "#e5e7eb" },
          legend: { orientation: "h", x: 0, y: 1.08 },
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
