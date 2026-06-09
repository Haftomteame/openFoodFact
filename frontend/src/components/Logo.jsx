import { Link } from "react-router-dom";

export default function Logo() {
  return (
    <Link to="/" className="logo-link">
      <div className="logo-magnifier">🔍</div>
      <div className="logo-wordmark">
        <span className="open">open </span>
        <span className="food">FOOD</span>
        <span className="facts"> facts</span>
      </div>
    </Link>
  );
}
