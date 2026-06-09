import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import Logo from "../components/Logo";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from || "/";
  const redirectState = location.state?.result ? { result: location.state.result } : undefined;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (user) return <Navigate to={redirectTo} state={redirectState} replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate(redirectTo, { state: redirectState });
    } catch (err) {
      setError(err.response?.data?.error || "Connexion impossible.");
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
          <h1 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>Connexion</h1>
          <p style={{ color: "var(--muted)", marginBottom: "1.25rem", fontSize: "0.9rem" }}>
            Connectez-vous pour enregistrer vos substituts.
          </p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">E-mail</label>
              <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label htmlFor="password">Mot de passe</label>
              <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {error && <p className="error">{error}</p>}
            <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%" }}>
              {loading ? "Connexion…" : "Se connecter"}
            </button>
          </form>
          <p style={{ marginTop: "1rem", textAlign: "center", fontSize: "0.9rem", color: "var(--muted)" }}>
            <Link to="/">Continuer sans connexion</Link>
            {" · "}
            <Link to="/register">Créer un compte</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
