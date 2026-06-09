export default function SearchToolbar({
  productCount,
  sortOrder,
  onSortChange,
  categories,
  activeCategory,
  onCategoryChange,
}) {
  const formattedCount = productCount.toLocaleString("fr-FR");

  return (
    <div className="search-toolbar">
      <div className="search-toolbar-inner">
        <div className="toolbar-count">
          <span>🔍</span>
          <span>{formattedCount} produit{productCount !== 1 ? "s" : ""}</span>
        </div>

        <button
          type="button"
          className="toolbar-btn"
          onClick={() => onSortChange(sortOrder === "asc" ? "desc" : "asc")}
          title="Trier par Nutri-Score"
        >
          ⇅ {sortOrder === "asc" ? "A → E" : "E → A"}
        </button>

        <div className="toolbar-filter">
          <span>☰</span>
          <select
            value={activeCategory}
            onChange={(e) => onCategoryChange(e.target.value)}
            aria-label="Explorer les produits par catégorie"
          >
            <option value="">Explorer les produits par…</option>
            {(Array.isArray(categories) ? categories : []).map((cat) => (
              <option key={cat.tag} value={cat.tag}>
                {cat.name_fr}
              </option>
            ))}
          </select>
          <span>▾</span>
        </div>
      </div>
    </div>
  );
}
