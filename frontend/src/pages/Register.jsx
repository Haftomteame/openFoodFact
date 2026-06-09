import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import Logo from "../components/Logo";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from || "/";
  const redirectState = location.state?.result ? { result: location.state.result } : undefined;
  const [form, setForm] = useState({ email: "", password: "", first_name: "", last_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (user) return <Navigate to={redirectTo} state={redirectState} replace />;

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      navigate(redirectTo, { state: redirectState });
    } catch (err) {
      const data = err.response?.data;
      setError(data?.email?.[0] || data?.password?.[0] || data?.error || "Inscription impossible.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <header className="site-header">
        <div className="header-inner" style={{ justifyContent: "center" }}>
          <Logo />
        </div>
      </header>
      <div className="container" style={{ maxWidth: 420, padding: "3rem 1rem" }}>
        <div className="card">
          <h1 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>Créer un compte</h1>
          <p style={{ color: "var(--muted)", marginBottom: "1.25rem", fontSize: "0.9rem" }}>
            Sauvegardez vos substituts alimentaires.
          </p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="first_name">Prénom</label>
              <input id="first_name" name="first_name" value={form.first_name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="last_name">Nom</label>
              <input id="last_name" name="last_name" value={form.last_name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="email">E-mail</label>
              <input id="email" name="email" type="email" value={form.email} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="password">Mot de passe</label>
              <input id="password" name="password" type="password" value={form.password} onChange={handleChange} required minLength={8} />
            </div>
            {error && <p className="error">{error}</p>}
            <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%" }}>
              {loading ? "Création…" : "S'inscrire"}
            </button>
          </form>
          <p style={{ marginTop: "1rem", textAlign: "center", fontSize: "0.9rem", color: "var(--muted)" }}>
            <Link to="/">Continuer sans compte</Link>
            {" · "}
            <Link to="/login">Se connecter</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
