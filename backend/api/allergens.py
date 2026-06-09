"""Allergènes alimentaires courants (14 réglementaires UE) et correspondance OFF."""

COMMON_ALLERGENS = [
    {"key": "gluten", "label_fr": "Gluten", "patterns": ["gluten"]},
    {"key": "milk", "label_fr": "Lait", "patterns": ["milk", "lait"]},
    {"key": "eggs", "label_fr": "Œufs", "patterns": ["eggs", "oeufs", "œufs"]},
    {"key": "nuts", "label_fr": "Fruits à coque", "patterns": ["nuts", "tree nuts", "fruits a coque"]},
    {"key": "peanuts", "label_fr": "Arachides", "patterns": ["peanuts", "arachides"]},
    {"key": "soybeans", "label_fr": "Soja", "patterns": ["soybeans", "soja", "soy"]},
    {"key": "fish", "label_fr": "Poisson", "patterns": ["fish", "poisson"]},
    {"key": "crustaceans", "label_fr": "Crustacés", "patterns": ["crustaceans", "crustaces"]},
    {"key": "celery", "label_fr": "Céleri", "patterns": ["celery", "celeri"]},
    {"key": "mustard", "label_fr": "Moutarde", "patterns": ["mustard", "moutarde"]},
    {"key": "sesame", "label_fr": "Sésame", "patterns": ["sesame"]},
    {
        "key": "sulphites",
        "label_fr": "Sulfites",
        "patterns": ["sulphur dioxide and sulphites", "sulphites", "sulfites"],
    },
    {"key": "lupin", "label_fr": "Lupin", "patterns": ["lupin"]},
    {"key": "molluscs", "label_fr": "Mollusques", "patterns": ["molluscs", "mollusques"]},
]

VALID_ALLERGEN_KEYS = {a["key"] for a in COMMON_ALLERGENS}
PATTERN_MAP = {a["key"]: a["patterns"] for a in COMMON_ALLERGENS}


def normalize_allergen(value: str) -> str:
    return value.lower().replace("-", " ").strip()


def product_has_allergens(product_allergens: list[str] | None, allergen_keys: list[str]) -> bool:
    if not allergen_keys or not product_allergens:
        return False

    normalized = {normalize_allergen(a) for a in product_allergens}
    for key in allergen_keys:
        if key not in PATTERN_MAP:
            continue
        for pattern in PATTERN_MAP[key]:
            pat = normalize_allergen(pattern)
            if any(pat in item or item in pat for item in normalized):
                return True
    return False
