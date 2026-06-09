import { ALLERGEN_OPTIONS } from "../constants/allergens";

function normalize(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/-/g, " ")
    .trim();
}

export function productHasAllergens(productAllergens, allergenKeys) {
  if (!allergenKeys?.length || !productAllergens?.length) return false;

  const normalizedProduct = productAllergens.map(normalize);
  return allergenKeys.some((key) => {
    const option = ALLERGEN_OPTIONS.find((item) => item.key === key);
    if (!option) return false;
    return option.patterns.some((pattern) => {
      const pat = normalize(pattern);
      return normalizedProduct.some((item) => item.includes(pat) || pat.includes(item));
    });
  });
}

export function filterProductsByAllergens(products, allergenKeys) {
  if (!allergenKeys?.length) return products;
  return products.filter((product) => !productHasAllergens(product.allergens, allergenKeys));
}

export function getMatchingAllergenLabels(productAllergens, allergenKeys) {
  if (!allergenKeys?.length || !productAllergens?.length) return [];
  return allergenKeys.filter((key) => productHasAllergens(productAllergens, [key]));
}
