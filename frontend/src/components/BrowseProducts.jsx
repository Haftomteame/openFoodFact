import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAllergy } from "../context/AllergyContext";
import { filterProductsByAllergens, productHasAllergens } from "../utils/allergens";
import { getRecentProducts } from "../utils/recentProducts";
import { foodApi } from "../services/api";
import AllergyBar from "./AllergyBar";
import PreferencesBar from "./PreferencesBar";
import ProductGrid from "./ProductGrid";
import RecentProducts from "./RecentProducts";
import SearchToolbar from "./SearchToolbar";

const DEFAULT_CATEGORY = "en:biscuits";
const NUTRI_RANK = { A: 1, B: 2, C: 3, D: 4, E: 5 };

export default function BrowseProducts() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { allergens, filterEnabled, hasAllergens } = useAllergy();
  const query = searchParams.get("q") || "";
  const categoryParam = searchParams.get("category") || "";

  const [categories, setCategories] = useState([]);
  const [activeTag, setActiveTag] = useState(categoryParam || DEFAULT_CATEGORY);
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sortHealthy, setSortHealthy] = useState(false);
  const [sortOrder, setSortOrder] = useState("asc");
  const [error, setError] = useState("");
  const [recentProducts, setRecentProducts] = useState(() => getRecentProducts());

  useEffect(() => {
    foodApi
      .getCategories()
      .then((res) => setCategories(Array.isArray(res.data) ? res.data : []))
      .catch(() =>
        setError(
          "Impossible de charger les catégories. Vérifiez VITE_API_URL sur Vercel (URL du backend Render).",
        ),
      );
  }, []);

  useEffect(() => {
    if (categoryParam) setActiveTag(categoryParam);
  }, [categoryParam]);

  useEffect(() => {
    setLoading(true);
    setError("");
    setSelectedProduct(null);

    const load = query
      ? foodApi.searchProducts(query)
      : foodApi.getCategoryProducts(activeTag);

    load
      .then((res) =>
        setProducts(Array.isArray(res.data?.products) ? res.data.products : []),
      )
      .catch(() =>
        setError(
          "Impossible de charger les produits. Vérifiez VITE_API_URL sur Vercel (URL du backend Render).",
        ),
      )
      .finally(() => setLoading(false));
  }, [activeTag, query]);

  useEffect(() => {
    setRecentProducts(getRecentProducts());
  }, [products]);

  const displayedProducts = useMemo(() => {
    let list = [...(Array.isArray(products) ? products : [])];
    if (filterEnabled && hasAllergens) {
      list = filterProductsByAllergens(list, allergens);
    }
    if (sortHealthy || sortOrder) {
      list.sort((a, b) => {
        const na = NUTRI_RANK[a.nutri_score?.toUpperCase()] || 99;
        const nb = NUTRI_RANK[b.nutri_score?.toUpperCase()] || 99;
        return sortOrder === "asc" ? na - nb : nb - na;
      });
    }
    return list;
  }, [products, sortHealthy, sortOrder, filterEnabled, hasAllergens, allergens]);

  const handleSubstitute = async () => {
    if (!selectedProduct) return;
    if (hasAllergens && productHasAllergens(selectedProduct.allergens, allergens)) {
      const proceed = window.confirm(
        "Ce produit contient un de vos allergènes. Voulez-vous quand même chercher un substitut sans ces allergènes ?",
      );
      if (!proceed) return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await foodApi.findSubstitute(selectedProduct.barcode, {
        avoidAllergens: hasAllergens,
        userAllergens: allergens,
      });
      navigate("/result", { state: { result: res.data } });
    } catch (err) {
      setError(err.response?.data?.error || "Aucun substitut trouvé.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <SearchToolbar
        productCount={displayedProducts.length}
        sortOrder={sortOrder}
        onSortChange={setSortOrder}
        categories={categories}
        activeCategory={query ? "" : activeTag}
        onCategoryChange={(tag) => {
          if (tag) {
            navigate(`/?category=${encodeURIComponent(tag)}`);
            setActiveTag(tag);
          }
        }}
      />

      <AllergyBar />

      <RecentProducts products={recentProducts} />

      <PreferencesBar
        productCount={displayedProducts.length}
        onSortByPreferences={setSortHealthy}
      />

      {query && (
        <p style={{ padding: "0.5rem 1.25rem 0", fontSize: "0.88rem", color: "var(--muted)" }}>
          Résultats pour « {query} »
        </p>
      )}

      {error && <p className="error" style={{ padding: "0 1.25rem" }}>{error}</p>}

      <ProductGrid
        products={displayedProducts}
        selectedBarcode={selectedProduct?.barcode}
        onSelect={setSelectedProduct}
        loading={loading && !products.length}
        userAllergens={allergens}
      />

      {selectedProduct && (
        <div className="sticky-action-bar">
          <Link
            to={`/product/${selectedProduct.barcode}`}
            className="btn btn-secondary"
            style={{ textDecoration: "none" }}
          >
            Voir la fiche
          </Link>
          <button
            type="button"
            className="btn btn-primary"
            disabled={loading}
            onClick={handleSubstitute}
          >
            {loading
              ? "Recherche du substitut…"
              : hasAllergens
                ? `Substitut sans vos allergènes pour « ${selectedProduct.name} »`
                : `Trouver un substitut pour « ${selectedProduct.name} »`}
          </button>
        </div>
      )}
    </div>
  );
}
