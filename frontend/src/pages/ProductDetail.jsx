import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import EcoScoreBadge from "../components/EcoScoreBadge";
import NovaBadge from "../components/NovaBadge";
import NutriScoreBar from "../components/NutriScoreBar";
import { ALLERGEN_LABELS } from "../constants/allergens";
import { useAllergy } from "../context/AllergyContext";
import { foodApi } from "../services/api";
import { addRecentProduct } from "../utils/recentProducts";
import { getMatchingAllergenLabels } from "../utils/allergens";

export default function ProductDetail() {
  const { barcode } = useParams();
  const navigate = useNavigate();
  const { allergens, hasAllergens } = useAllergy();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [finding, setFinding] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError("");
    foodApi
      .getProductByBarcode(barcode)
      .then((res) => {
        setProduct(res.data);
        addRecentProduct(res.data);
      })
      .catch((err) => {
        setError(err.response?.data?.error || "Produit introuvable.");
      })
      .finally(() => setLoading(false));
  }, [barcode]);

  const handleSubstitute = async () => {
    setFinding(true);
    setError("");
    try {
      const res = await foodApi.findSubstitute(barcode, {
        avoidAllergens: hasAllergens,
        userAllergens: allergens,
      });
      navigate("/result", { state: { result: res.data } });
    } catch (err) {
      setError(err.response?.data?.error || "Aucun substitut trouvé.");
    } finally {
      setFinding(false);
    }
  };

  if (loading) return <p className="loading-text">Chargement de la fiche produit…</p>;
  if (error && !product) {
    return (
      <div style={{ padding: "2rem 1.25rem" }}>
        <p className="error">{error}</p>
        <Link to="/">← Retour à l'accueil</Link>
      </div>
    );
  }

  const matchingAllergens = getMatchingAllergenLabels(product.allergens, allergens);

  return (
    <div className="product-detail">
      <button type="button" className="btn btn-ghost" onClick={() => navigate(-1)}>
        ← Retour
      </button>

      <div className="product-detail-grid">
        <div className="product-detail-image card">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} />
          ) : (
            <span style={{ fontSize: "4rem", opacity: 0.2 }}>🍽️</span>
          )}
        </div>

        <div className="product-detail-info">
          <h1>{product.name}</h1>
          {product.brand && <p className="detail-brand">{product.brand}</p>}
          {product.quantity && <p className="detail-quantity">{product.quantity}</p>}
          {product.category_name && (
            <p className="detail-category">Catégorie : {product.category_name}</p>
          )}

          <div className="detail-scores">
            <NutriScoreBar score={product.nutri_score} />
            <NovaBadge group={product.nova_group} />
            <EcoScoreBadge grade={product.ecoscore_grade} />
          </div>

          {matchingAllergens.length > 0 && (
            <p className="product-allergy-warning detail-warning">
              ⚠ Contient : {matchingAllergens.map((key) => ALLERGEN_LABELS[key]).join(", ")}
            </p>
          )}

          {product.allergens?.length > 0 && (
            <div className="detail-block">
              <h3>Allergènes déclarés</h3>
              <p>{product.allergens.join(", ")}</p>
            </div>
          )}

          {product.ingredients_text && (
            <div className="detail-block">
              <h3>Ingrédients</h3>
              <p className="detail-ingredients">{product.ingredients_text}</p>
            </div>
          )}

          {product.stores?.length > 0 && (
            <div className="detail-block">
              <h3>Où l'acheter</h3>
              <p>{product.stores.join(", ")}</p>
            </div>
          )}

          <div className="detail-actions">
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSubstitute}
              disabled={finding}
            >
              {finding
                ? "Recherche…"
                : hasAllergens
                  ? "Trouver un substitut sans mes allergènes"
                  : "Trouver un substitut plus sain"}
            </button>
            {product.off_url && (
              <a
                href={product.off_url}
                target="_blank"
                rel="noreferrer"
                className="btn btn-secondary"
                style={{ textDecoration: "none" }}
              >
                Voir sur Open Food Facts
              </a>
            )}
          </div>

          {error && <p className="error">{error}</p>}
        </div>
      </div>
    </div>
  );
}
