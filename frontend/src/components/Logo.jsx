import { Link } from "react-router-dom";

export default function Logo() {
  return (
    <Link to="/" className="logo-link">
      <div className="logo-magnifier">🔍</div>
      <div className="logo-wordmark">
        <span className="food">Food</span>
        <span className="facts">Facts</span>
        <span className="hub"> Hub</span>
      </div>
    </Link>
  );
}
