const STORAGE_KEY = "pur_beurre_recent_products";
const MAX_ITEMS = 8;

export function addRecentProduct(product) {
  if (!product?.barcode) return;

  try {
    const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    const filtered = existing.filter((item) => item.barcode !== product.barcode);
    const next = [
      {
        barcode: product.barcode,
        name: product.name,
        brand: product.brand,
        image_url: product.image_url,
        nutri_score: product.nutri_score,
        viewed_at: new Date().toISOString(),
      },
      ...filtered,
    ].slice(0, MAX_ITEMS);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    /* ignore */
  }
}

export function getRecentProducts() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}
