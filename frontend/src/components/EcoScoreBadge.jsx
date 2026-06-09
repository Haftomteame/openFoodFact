export default function EcoScoreBadge({ grade }) {
  if (!grade) {
    return (
      <span className="eco-badge eco-unknown" title="Eco-Score inconnu">
        🌿 ?
      </span>
    );
  }
  const g = grade.toUpperCase();
  return (
    <span className={`eco-badge eco-${g.toLowerCase()}`} title={`Eco-Score ${g}`}>
      🌿 {g}
    </span>
  );
}
