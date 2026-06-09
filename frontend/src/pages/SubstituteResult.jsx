import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import NutriCompare from "../components/NutriCompare";
import ProductCard from "../components/ProductCard";
import { useAllergy } from "../context/AllergyContext";
import { useAuth } from "../context/AuthContext";
import { nutriImprovement } from "../utils/nutrition";
import { foodApi } from "../services/api";

export default function SubstituteResult() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { allergens } = useAllergy();
  const initialResult = location.state?.result;
  const [result, setResult] = useState(initialResult);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  if (!result?.success) {
    return (
      <div style={{ padding: "2rem 0" }}>
        <p className="error">{result?.error || "Résultat indisponible."}</p>
        <Link to="/">← Retour à l'accueil</Link>
      </div>
    );
  }

  const { original, substitute, reason, alternatives = [], improvement } = result;

  const handleSave = async () => {
    if (!user) {
      navigate("/login", { state: { from: "/result", result } });
      return;
    }
    setSaving(true);
    setError("");
    try {
      await foodApi.saveSubstitution(original.barcode, substitute.barcode, reason);
      setSaved(true);
    } catch {
      setError("Impossible d'enregistrer la substitution.");
    } finally {
      setSaving(false);
    }
  };

  const handlePickAlternative = (alt) => {
    setResult((prev) => ({
      ...prev,
      substitute: alt,
      reason: `Alternative sélectionnée — Nutri-Score ${prev.original?.nutri_score || "?"} → ${alt.nutri_score || "?"}.`,
      improvement: {
        nutri_score_before: prev.original?.nutri_score,
        nutri_score_after: alt.nutri_score,
        nutri_steps: nutriImprovement(prev.original?.nutri_score, alt.nutri_score),
        nova_delta:
          prev.original?.nova_group && alt.nova_group
            ? prev.original.nova_group - alt.nova_group
            : null,
      },
    }));
    setSaved(false);
  };

  return (
    <div style={{ padding: "1rem 0 2rem" }}>
      <button type="button" className="btn btn-ghost" onClick={() => navigate(-1)}>
        ← Retour
      </button>

      <h1 style={{ margin: "1rem 0 0.25rem", fontSize: "1.35rem" }}>
        Substitut recommandé
      </h1>
      <p style={{ color: "var(--muted)", marginBottom: "1rem", fontSize: "0.95rem" }}>
        {reason}
      </p>

      {result.allergy_safe && (
        <p className="allergy-safe-banner">
          ✓ Ce substitut est compatible avec vos allergènes déclarés.
        </p>
      )}

      <NutriCompare original={original} substitute={substitute} improvement={improvement} />

      <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
        <div>
          <p style={{ fontSize: "0.85rem", color: "var(--muted)", marginBottom: "0.5rem" }}>
            Produit d'origine
          </p>
          <ProductCard product={original} userAllergens={allergens} />
        </div>
        <div>
          <p style={{ fontSize: "0.85rem", color: "var(--muted)", marginBottom: "0.5rem" }}>
            Substitut proposé
          </p>
          <ProductCard product={substitute} userAllergens={allergens} />
        </div>
      </div>

      {alternatives.length > 0 && (
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <h3 style={{ fontSize: "1rem", marginBottom: "0.75rem" }}>Autres alternatives</h3>
          <div className="alternatives-grid">
            {alternatives.map((alt) => (
              <button
                key={alt.barcode}
                type="button"
                className="alternative-card"
                onClick={() => handlePickAlternative(alt)}
              >
                <ProductCard product={alt} userAllergens={allergens} />
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ fontSize: "1rem", marginBottom: "0.75rem" }}>Description</h3>
        <p style={{ lineHeight: 1.6, fontSize: "0.95rem" }}>{substitute.description}</p>

        {substitute.stores?.length > 0 && (
          <>
            <h3 style={{ fontSize: "1rem", margin: "1rem 0 0.5rem" }}>Où l'acheter</h3>
            <p style={{ fontSize: "0.95rem" }}>{substitute.stores.join(", ")}</p>
          </>
        )}

        {substitute.off_url && (
          <p style={{ marginTop: "1rem" }}>
            <a href={substitute.off_url} target="_blank" rel="noreferrer">
              Voir sur Open Food Facts →
            </a>
          </p>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      <div className="page-actions">
        <Link
          to={`/product/${original.barcode}`}
          className="btn btn-secondary"
          style={{ textDecoration: "none" }}
        >
          Fiche produit d'origine
        </Link>
        {user ? (
          <>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSave}
              disabled={saved || saving}
            >
              {saved ? "✓ Enregistré" : saving ? "Enregistrement…" : "Enregistrer ce substitut"}
            </button>
            <Link to="/substitutions" className="btn btn-secondary" style={{ textDecoration: "none" }}>
              Mes substituts
            </Link>
          </>
        ) : (
          <>
            <Link
              to="/login"
              state={{ from: "/result", result }}
              className="btn btn-primary"
              style={{ textDecoration: "none" }}
            >
              Se connecter pour enregistrer
            </Link>
            <Link
              to="/register"
              state={{ from: "/result", result }}
              className="btn btn-secondary"
              style={{ textDecoration: "none" }}
            >
              Créer un compte
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
