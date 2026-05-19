import Plot from "react-plotly.js";
import type { PlotMouseEvent } from "plotly.js";
import type { AnalyzedOpinion } from "../types/opinion";

interface OpinionMapProps {
  opinions: AnalyzedOpinion[];
  selectedOpinionId?: string;
  onSelectOpinion: (opinion: AnalyzedOpinion) => void;
}

const responseTypeColors: Record<string, string> = {
  "주관식": "#2563eb",
  "객관식-단일": "#059669",
  "객관식-복수": "#7c3aed"
};

export default function OpinionMap({ opinions, selectedOpinionId, onSelectOpinion }: OpinionMapProps) {
  const responseTypes = ["주관식", "객관식-단일", "객관식-복수"];

  const data = responseTypes.map((responseType) => {
    const group = opinions.filter((opinion) => opinion.responseType === responseType);
    return {
      type: "scatter" as const,
      mode: "markers" as const,
      name: responseType,
      x: group.map((opinion) => opinion.x),
      y: group.map((opinion) => opinion.y),
      text: group.map((opinion) => `${opinion.id}<br>${opinion.responseType} / ${opinion.category}<br>${opinion.text}`),
      customdata: group.map((opinion) => [opinion.id]),
      hovertemplate: "%{text}<extra></extra>",
      marker: {
        color: responseTypeColors[responseType],
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
    const point = event.points[0];
    const traceCustomData = point?.data?.customdata as (string[] | string)[] | undefined;
    const fallbackCustomData = typeof point?.pointNumber === "number" ? traceCustomData?.[point.pointNumber] : undefined;
    const rawCustomData = (point?.customdata ?? fallbackCustomData) as string[] | string | undefined;
    const id = Array.isArray(rawCustomData) ? rawCustomData[0] : rawCustomData;
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
