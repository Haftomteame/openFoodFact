import re
from typing import Any


class DataCleaner:
    """Nettoie et normalise les données brutes de l'API Open Food Facts."""

    NUTRI_SCORE_MAP = {
        "unknown": None,
        "not-applicable": None,
    }

    @classmethod
    def clean_product(cls, raw: dict[str, Any]) -> dict[str, Any]:
        barcode = str(raw.get("code", "")).strip()
        name = cls._clean_text(
            raw.get("product_name")
            or raw.get("product_name_fr")
            or raw.get("generic_name")
            or "Produit sans nom"
        )
        brand = cls._clean_text(raw.get("brands", "").split(",")[0] if raw.get("brands") else "")
        category_tag, category_name = cls._extract_category(raw)
        nutri_score = cls._normalize_nutri_score(
            raw.get("nutriscore_grade") or raw.get("nutrition_grades")
        )
        ecoscore_grade = cls._normalize_nutri_score(raw.get("ecoscore_grade"))
        nova_group = cls._safe_int(raw.get("nova_group"))
        allergens = cls._clean_allergens(raw.get("allergens_tags", []))
        ingredients = cls._clean_text(
            raw.get("ingredients_text_fr") or raw.get("ingredients_text") or ""
        )
        image_url = raw.get("image_front_url") or raw.get("image_url") or ""
        off_url = raw.get("url") or f"https://world.openfoodfacts.org/product/{barcode}"
        stores = cls._clean_stores(raw)
        countries = cls._clean_tags(raw.get("countries_tags", []))

        return {
            "barcode": barcode,
            "name": name,
            "brand": brand,
            "category_tag": category_tag,
            "category_name": category_name,
            "nutri_score": nutri_score,
            "ecoscore_grade": ecoscore_grade,
            "nova_group": nova_group,
            "allergens": allergens,
            "ingredients_text": ingredients,
            "image_url": image_url,
            "off_url": off_url,
            "stores": stores,
            "countries": countries,
            "quantity": cls._clean_text(raw.get("quantity") or raw.get("product_quantity") or ""),
        }

    @classmethod
    def _clean_text(cls, value: Any) -> str:
        if not value:
            return ""
        text = str(value).strip()
        text = re.sub(r"\s+", " ", text)
        return text

    @classmethod
    def _extract_category(cls, raw: dict[str, Any]) -> tuple[str, str]:
        tags = raw.get("categories_tags") or []
        names_fr = raw.get("categories_tags_fr") or []
        categories = raw.get("categories", "")

        if tags:
            tag = tags[0]
            name = names_fr[0] if names_fr else categories.split(",")[0].strip() if categories else tag
            return tag, cls._clean_text(name)
        if categories:
            first = categories.split(",")[0].strip()
            return "", cls._clean_text(first)
        return "", "Non catégorisé"

    @classmethod
    def _normalize_nutri_score(cls, value: Any) -> str | None:
        if not value:
            return None
        score = str(value).strip().lower()
        if score in cls.NUTRI_SCORE_MAP:
            return None
        if score in ("a", "b", "c", "d", "e"):
            return score.upper()
        return None

    @classmethod
    def _safe_int(cls, value: Any) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _clean_allergens(cls, tags: list) -> list[str]:
        allergens = []
        for tag in tags or []:
            if isinstance(tag, str) and tag.startswith("en:"):
                allergens.append(tag.replace("en:", "").replace("-", " ").title())
        return allergens

    @classmethod
    def _clean_tags(cls, tags: list) -> list[str]:
        return [
            t.replace("en:", "").replace("-", " ").title()
            for t in (tags or [])
            if isinstance(t, str)
        ]

    @classmethod
    def _clean_stores(cls, raw: dict[str, Any]) -> list[str]:
        stores: list[str] = []
        for field in ("stores", "purchase_places"):
            value = raw.get(field)
            if value:
                parts = [s.strip() for s in str(value).split(",") if s.strip()]
                stores.extend(parts)
        seen = set()
        unique = []
        for store in stores:
            key = store.lower()
            if key not in seen:
                seen.add(key)
                unique.append(store)
        return unique[:10]
