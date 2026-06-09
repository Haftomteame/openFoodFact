import NutriScoreBar from "./NutriScoreBar";
import NovaBadge from "./NovaBadge";
import EcoScoreBadge from "./EcoScoreBadge";
import { nutriImprovement } from "../utils/nutrition";

export default function NutriCompare({ original, substitute, improvement }) {
  const steps =
    improvement?.nutri_steps ??
    nutriImprovement(original?.nutri_score, substitute?.nutri_score);

  return (
    <div className="nutri-compare card">
      <h3 style={{ fontSize: "1rem", marginBottom: "1rem" }}>Comparateur nutritionnel</h3>

      <div className="compare-grid">
        <div className="compare-col">
          <p className="compare-label">Avant</p>
          <p className="compare-name">{original?.name}</p>
          <NutriScoreBar score={original?.nutri_score} />
          <div className="compare-badges">
            <NovaBadge group={original?.nova_group} />
            <EcoScoreBadge grade={original?.ecoscore_grade} />
          </div>
        </div>

        <div className="compare-arrow" aria-hidden="true">
          {steps > 0 ? (
            <span className="compare-improvement">+{steps} niveau{steps > 1 ? "x" : ""}</span>
          ) : (
            <span>→</span>
          )}
        </div>

        <div className="compare-col">
          <p className="compare-label">Après</p>
          <p className="compare-name">{substitute?.name}</p>
          <NutriScoreBar score={substitute?.nutri_score} />
          <div className="compare-badges">
            <NovaBadge group={substitute?.nova_group} />
            <EcoScoreBadge grade={substitute?.ecoscore_grade} />
          </div>
        </div>
      </div>

      {improvement?.nova_delta > 0 && (
        <p className="compare-note">
          NOVA : {original?.nova_group} → {substitute?.nova_group} (moins ultra-transformé)
        </p>
      )}
    </div>
  );
}
