import EcoScoreBadge from "./EcoScoreBadge";
import NutriScoreBar from "./NutriScoreBar";
import NovaBadge from "./NovaBadge";

function formatTitle(product) {
  const parts = [product.name];
  if (product.brand) parts.push(product.brand);
  if (product.quantity) parts.push(product.quantity);
  return parts.join(" – ");
}

export default function ProductCard({ product, selected, onSelect }) {
  const title = formatTitle(product);
  const Wrapper = onSelect ? "button" : "article";

  return (
    <Wrapper
      type={onSelect ? "button" : undefined}
      onClick={() => onSelect?.(product)}
      className={`product-card${selected ? " selected" : ""}`}
    >
      <div className="product-card-image">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} loading="lazy" />
        ) : (
          <span style={{ fontSize: "3rem", opacity: 0.2 }}>🍽️</span>
        )}
      </div>
      <div className="product-card-body">
        <p className="product-card-title">{title}</p>
        <div className="product-card-scores">
          <NutriScoreBar score={product.nutri_score} />
          <NovaBadge group={product.nova_group} />
          <EcoScoreBadge grade={product.ecoscore_grade} />
        </div>
      </div>
    </Wrapper>
  );
}
