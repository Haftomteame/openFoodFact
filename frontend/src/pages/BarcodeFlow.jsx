import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAllergy } from "../context/AllergyContext";
import { productHasAllergens } from "../utils/allergens";
import ProductCard from "../components/ProductCard";
import { foodApi } from "../services/api";
import { addRecentProduct } from "../utils/recentProducts";

export default function BarcodeFlow() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { allergens, hasAllergens } = useAllergy();
  const [barcode, setBarcode] = useState(searchParams.get("q") || "");
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const q = searchParams.get("q");
    if (q && /^\d{8,14}$/.test(q.replace(/\s/g, ""))) {
      setBarcode(q.replace(/\s/g, ""));
      lookup(q.replace(/\s/g, ""));
    }
  }, [searchParams]);

  const lookup = async (code) => {
    setError("");
    setProduct(null);
    setLoading(true);
    try {
      const res = await foodApi.getProductByBarcode(code);
      setProduct(res.data);
      addRecentProduct(res.data);
    } catch (err) {
      setError(err.response?.data?.error || "Produit introuvable.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    await lookup(barcode.trim());
  };

  const handleSubstitute = async () => {
    if (product && hasAllergens && productHasAllergens(product.allergens, allergens)) {
      const proceed = window.confirm(
        "Ce produit contient un de vos allergènes. Chercher un substitut sans ces allergènes ?",
      );
      if (!proceed) return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await foodApi.findSubstitute(barcode.trim(), {
        avoidAllergens: hasAllergens,
        userAllergens: allergens,
      });
      navigate("/result", { state: { result: res.data } });
    } catch (err) {
      setError(err.response?.data?.error || "Aucun substitut trouvé.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: "2rem auto" }}>
      <h1 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>Recherche par code-barres</h1>
      <p style={{ color: "var(--muted)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
        Exemple Nutella : 8000500310427
      </p>

      <form onSubmit={handleSearch} className="card" style={{ marginBottom: "1.5rem" }}>
        <div className="form-group">
          <label htmlFor="barcode">Code-barres (EAN)</label>
          <input
            id="barcode"
            value={barcode}
            onChange={(e) => setBarcode(e.target.value.replace(/\D/g, ""))}
            placeholder="8000500310427"
            maxLength={14}
            required
          />
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Recherche…" : "Rechercher"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {product && (
        <div>
          <div style={{ maxWidth: 280, margin: "0 auto 1rem" }}>
            <ProductCard product={product} userAllergens={allergens} />
          </div>
          <div className="page-actions" style={{ justifyContent: "center" }}>
            <Link
              to={`/product/${product.barcode}`}
              className="btn btn-secondary"
              style={{ textDecoration: "none" }}
            >
              Voir la fiche complète
            </Link>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSubstitute}
              disabled={loading}
            >
              {loading
                ? "Recherche…"
                : hasAllergens
                  ? "Substitut sans mes allergènes"
                  : "Proposer un substitut plus sain"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
