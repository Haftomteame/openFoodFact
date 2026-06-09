import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { foodApi } from "../services/api";

export default function MySubstitutions() {
  const [substitutions, setSubstitutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    foodApi
      .getMySubstitutions()
      .then((res) => setSubstitutions(res.data))
      .catch(() => setError("Impossible de charger vos substituts."))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id) => {
    try {
      await foodApi.deleteSubstitution(id);
      setSubstitutions((prev) => prev.filter((s) => s.id !== id));
    } catch {
      setError("Suppression impossible.");
    }
  };

  return (
    <div style={{ padding: "1rem 0 2rem" }}>
      <h1 style={{ fontSize: "1.35rem", marginBottom: "0.25rem" }}>Mes aliments substitués</h1>
      <p style={{ color: "var(--muted)", marginBottom: "1.5rem", fontSize: "0.95rem" }}>
        Vos alternatives enregistrées.
      </p>

      {loading && <p className="loading-text">Chargement…</p>}
      {error && <p className="error">{error}</p>}

      {!loading && substitutions.length === 0 && (
        <div className="card">
          <p>Aucun substitut enregistré.</p>
          <Link to="/">Parcourir les produits →</Link>
        </div>
      )}

      <div className="product-grid">
        {substitutions.map((sub) => (
          <article key={sub.id} className="product-card" style={{ cursor: "default" }}>
            <div className="product-card-body">
              <p style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
                {new Date(sub.saved_at).toLocaleDateString("fr-FR")}
              </p>
              <p className="product-card-title">
                <strong>{sub.original_name}</strong>
                <br />→ <strong>{sub.substitute_name}</strong>
              </p>
              <p style={{ fontSize: "0.85rem", color: "var(--muted)", margin: 0 }}>
                {sub.substitute_description}
              </p>
              {sub.substitute_off_url && (
                <a href={sub.substitute_off_url} target="_blank" rel="noreferrer" style={{ fontSize: "0.85rem" }}>
                  Open Food Facts →
                </a>
              )}
              <button
                type="button"
                className="btn btn-ghost"
                style={{ marginTop: "0.5rem", alignSelf: "flex-start" }}
                onClick={() => handleDelete(sub.id)}
              >
                Supprimer
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
