import { ALLERGEN_OPTIONS } from "../constants/allergens";
import { useAllergy } from "../context/AllergyContext";

export default function AllergyBar() {
  const { allergens, filterEnabled, toggleAllergen, setAllergyFilter, hasAllergens } =
    useAllergy();

  return (
    <div className="allergy-bar">
      <div className="allergy-inner">
        <div className="allergy-header">
          <span className="allergy-title">🛡️ Mode allergies alimentaires</span>
          <div className="preferences-inner" style={{ marginLeft: "auto" }}>
            <button
              type="button"
              className={`toggle-switch${filterEnabled ? " on" : ""}`}
              onClick={() => setAllergyFilter(!filterEnabled)}
              aria-pressed={filterEnabled}
              disabled={!hasAllergens}
              title={
                hasAllergens
                  ? "Masquer les produits contenant vos allergènes"
                  : "Sélectionnez d'abord vos allergènes"
              }
            />
            <span>Masquer les produits à éviter</span>
          </div>
        </div>

        <p className="allergy-help">
          Sélectionnez vos allergènes pour filtrer les produits et trouver des substituts compatibles.
        </p>

        <div className="allergy-chips">
          {ALLERGEN_OPTIONS.map((option) => {
            const active = allergens.includes(option.key);
            return (
              <button
                key={option.key}
                type="button"
                className={`allergy-chip${active ? " active" : ""}`}
                onClick={() => toggleAllergen(option.key)}
                aria-pressed={active}
              >
                {option.label}
              </button>
            );
          })}
        </div>

        {hasAllergens && (
          <p className="allergy-summary">
            {allergens.length} allergène{allergens.length > 1 ? "s" : ""} sélectionné
            {allergens.length > 1 ? "s" : ""}
            {filterEnabled ? " — filtrage actif" : ""}
          </p>
        )}
      </div>
    </div>
  );
}
