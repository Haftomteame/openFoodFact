import NutriScoreBar from "./NutriScoreBar";

export default function NutriScore({ score }) {
  if (!score) {
    return <span style={{ fontSize: "0.85rem", color: "var(--muted)" }}>Nutri-Score inconnu</span>;
  }
  return <NutriScoreBar score={score} />;
}
