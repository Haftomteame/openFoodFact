import EcoScoreBadge from "./EcoScoreBadge";
import NutriScoreBar from "./NutriScoreBar";
import NovaBadge from "./NovaBadge";
import { ALLERGEN_LABELS } from "../constants/allergens";
import { getMatchingAllergenLabels } from "../utils/allergens";

function formatTitle(product) {
  const parts = [product.name];
  if (product.brand) parts.push(product.brand);
  if (product.quantity) parts.push(product.quantity);
  return parts.join(" – ");
}

export default function ProductCard({ product, selected, onSelect, userAllergens = [] }) {
  const title = formatTitle(product);
  const Wrapper = onSelect ? "button" : "article";
  const matchingAllergens = getMatchingAllergenLabels(product.allergens, userAllergens);
  const hasAllergyConflict = matchingAllergens.length > 0;

  return (
    <Wrapper
      type={onSelect ? "button" : undefined}
      onClick={() => onSelect?.(product)}
      className={`product-card${selected ? " selected" : ""}${hasAllergyConflict ? " allergy-conflict" : ""}`}
    >
      <div className="product-card-image">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} loading="lazy" />
        ) : (
          <span style={{ fontSize: "3rem", opacity: 0.2 }}>🍽️</span>
        )}
        {hasAllergyConflict && (
          <span className="allergy-badge" title="Contient un de vos allergènes">
            ⚠ Allergène
          </span>
        )}
      </div>
      <div className="product-card-body">
        <p className="product-card-title">{title}</p>
        <div className="product-card-scores">
          <NutriScoreBar score={product.nutri_score} />
          <NovaBadge group={product.nova_group} />
          <EcoScoreBadge grade={product.ecoscore_grade} />
        </div>
        {product.allergens?.length > 0 && (
          <p className="product-allergens">
            Allergènes : {product.allergens.slice(0, 3).join(", ")}
            {product.allergens.length > 3 ? "…" : ""}
          </p>
        )}
        {hasAllergyConflict && (
          <p className="product-allergy-warning">
            Contient : {matchingAllergens.map((key) => ALLERGEN_LABELS[key]).join(", ")}
          </p>
        )}
      </div>
    </Wrapper>
  );
}
