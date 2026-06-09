import ProductCard from "./ProductCard";

export default function ProductGrid({ products, selectedBarcode, onSelect, loading }) {
  if (loading) {
    return <p className="loading-text">Chargement des produits…</p>;
  }

  if (!products?.length) {
    return (
      <p className="loading-text">Aucun produit trouvé dans cette catégorie.</p>
    );
  }

  return (
    <div className="product-grid">
      {products.map((product) => (
        <ProductCard
          key={product.barcode}
          product={product}
          selected={selectedBarcode === product.barcode}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
