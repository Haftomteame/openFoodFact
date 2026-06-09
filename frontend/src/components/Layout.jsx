import { useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Logo from "./Logo";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const trimmed = search.trim();
    const digits = trimmed.replace(/\s/g, "");
    if (/^\d{8,14}$/.test(digits)) {
      navigate(`/barcode?q=${digits}`);
    } else if (trimmed) {
      navigate(`/?q=${encodeURIComponent(trimmed)}`);
    }
  };

  return (
    <div>
      <header className="site-header">
        <div className="header-top">
          <Logo />

          <div className="header-search-wrap">
            <form className="header-search" onSubmit={handleSearch}>
              <input
                type="search"
                placeholder="Chercher un produit"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <button type="submit" aria-label="Rechercher">🔍</button>
            </form>
          </div>

          <nav className="header-nav">
            <Link to="/">Découvrir</Link>
            <Link to="/register">Contribuer</Link>
            {user ? (
              <div className="user-menu">
                <Link to="/substitutions">Mes substituts</Link>
                <span style={{ color: "var(--muted)" }}>{user.first_name || user.email}</span>
                <button type="button" className="btn btn-ghost" onClick={handleLogout}>
                  Déconnexion
                </button>
              </div>
            ) : (
              <Link to="/login">Connexion</Link>
            )}
          </nav>
        </div>

        <div className="header-sub">
          <Link to="/?world=1">→ Voir les résultats du monde entier</Link>
        </div>
      </header>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
