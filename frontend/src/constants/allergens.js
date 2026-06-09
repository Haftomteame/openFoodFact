export const ALLERGEN_OPTIONS = [
  { key: "gluten", label: "Gluten", patterns: ["gluten"] },
  { key: "milk", label: "Lait", patterns: ["milk", "lait"] },
  { key: "eggs", label: "Œufs", patterns: ["eggs", "oeufs", "œufs"] },
  { key: "nuts", label: "Fruits à coque", patterns: ["nuts", "tree nuts", "fruits a coque"] },
  { key: "peanuts", label: "Arachides", patterns: ["peanuts", "arachides"] },
  { key: "soybeans", label: "Soja", patterns: ["soybeans", "soja", "soy"] },
  { key: "fish", label: "Poisson", patterns: ["fish", "poisson"] },
  { key: "crustaceans", label: "Crustacés", patterns: ["crustaceans", "crustaces"] },
  { key: "celery", label: "Céleri", patterns: ["celery", "celeri"] },
  { key: "mustard", label: "Moutarde", patterns: ["mustard", "moutarde"] },
  { key: "sesame", label: "Sésame", patterns: ["sesame"] },
  {
    key: "sulphites",
    label: "Sulfites",
    patterns: ["sulphur dioxide and sulphites", "sulphites", "sulfites"],
  },
  { key: "lupin", label: "Lupin", patterns: ["lupin"] },
  { key: "molluscs", label: "Mollusques", patterns: ["molluscs", "mollusques"] },
];

export const ALLERGEN_LABELS = Object.fromEntries(
  ALLERGEN_OPTIONS.map((item) => [item.key, item.label]),
);
