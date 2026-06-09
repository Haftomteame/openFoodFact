const GRADES = ["A", "B", "C", "D", "E"];

export default function NutriScoreBar({ score }) {
  const active = score?.toUpperCase();

  return (
    <div className="nutri-scale" title="Nutri-Score">
      {GRADES.map((g) => (
        <span key={g} className={`n-${g.toLowerCase()}${active === g ? " active" : ""}`}>
          {g}
        </span>
      ))}
    </div>
  );
}
