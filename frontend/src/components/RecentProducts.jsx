import { Link } from "react-router-dom";
import NutriScoreBar from "./NutriScoreBar";

export default function RecentProducts({ products }) {
  if (!products?.length) return null;

  return (
    <section className="recent-section">
      <div className="recent-inner">
        <h2 className="recent-title">Consultés récemment</h2>
        <div className="recent-list">
          {products.map((product) => (
            <Link
              key={product.barcode}
              to={`/product/${product.barcode}`}
              className="recent-item"
            >
              <div className="recent-thumb">
                {product.image_url ? (
                  <img src={product.image_url} alt="" loading="lazy" />
                ) : (
                  <span>🍽️</span>
                )}
              </div>
              <div className="recent-meta">
                <p className="recent-name">{product.name}</p>
                {product.brand && <p className="recent-brand">{product.brand}</p>}
                <NutriScoreBar score={product.nutri_score} />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
