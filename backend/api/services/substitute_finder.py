from typing import Any

from api.services.data_cleaner import DataCleaner
from api.services.off_client import OpenFoodFactsClient
from api.services.repository import ProductRepository

NUTRI_RANK = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


class SubstituteFinder:
    """Propose un substitut plus sain pour un produit donné."""

    def __init__(
        self,
        off_client: OpenFoodFactsClient | None = None,
        repository: ProductRepository | None = None,
    ):
        self.off_client = off_client or OpenFoodFactsClient()
        self.repository = repository or ProductRepository()

    def find_substitute(
        self,
        barcode: str | None = None,
        product_data: dict[str, Any] | None = None,
        avoid_allergens: bool = True,
    ) -> dict[str, Any]:
        original = self._resolve_original(barcode, product_data)
        if not original:
            return {"success": False, "error": "Produit introuvable."}

        category_tag = original.get("category_tag")
        if not category_tag:
            return {
                "success": False,
                "error": "Catégorie du produit inconnue. Impossible de proposer un substitut.",
                "original": original,
            }

        candidates_raw = self.off_client.find_better_in_category(
            category_tag=category_tag,
            max_nutri_score=original.get("nutri_score") or "E",
            exclude_barcode=original.get("barcode"),
        )

        if not candidates_raw:
            candidates_raw = self.off_client.search_products_by_category(
                category_tag=category_tag,
                page_size=30,
            )
            candidates_raw = [
                p
                for p in candidates_raw
                if p.get("code") != original.get("barcode")
            ]

        cleaned_candidates = [DataCleaner.clean_product(p) for p in candidates_raw]
        cleaned_candidates = [c for c in cleaned_candidates if c["barcode"]]

        if avoid_allergens and original.get("allergens"):
            original_allergens = {a.lower() for a in original["allergens"]}
            filtered = [
                c
                for c in cleaned_candidates
                if not original_allergens.intersection({a.lower() for a in c.get("allergens", [])})
            ]
            if filtered:
                cleaned_candidates = filtered

        substitute = self._pick_best(cleaned_candidates, original)
        if not substitute:
            return {
                "success": False,
                "error": "Aucun substitut plus sain trouvé dans cette catégorie.",
                "original": original,
            }

        self.repository.upsert_product(original)
        self.repository.upsert_product(substitute)

        reason = self._build_reason(original, substitute)

        return {
            "success": True,
            "original": self._to_response(original),
            "substitute": {
                **self._to_response(substitute),
                "description": self._build_description(substitute, original),
            },
            "reason": reason,
        }

    def _resolve_original(
        self,
        barcode: str | None,
        product_data: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        if product_data:
            return product_data

        if not barcode:
            return None

        cached = self.repository.get_product_by_barcode(barcode)
        if cached:
            return self._product_to_dict(cached)

        raw = self.off_client.get_product_by_barcode(barcode)
        if raw:
            cleaned = DataCleaner.clean_product(raw)
            self.repository.upsert_product(cleaned)
            return cleaned
        return None

    def _pick_best(
        self,
        candidates: list[dict[str, Any]],
        original: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not candidates:
            return None

        original_rank = NUTRI_RANK.get(original.get("nutri_score") or "E", 5)

        def score(candidate: dict[str, Any]) -> tuple:
            nutri = NUTRI_RANK.get(candidate.get("nutri_score") or "E", 5)
            has_stores = 0 if candidate.get("stores") else 1
            has_image = 0 if candidate.get("image_url") else 1
            return (nutri, has_stores, has_image)

        better = [c for c in candidates if score(c)[0] < original_rank]
        pool = better if better else candidates
        return min(pool, key=score)

    def _build_reason(self, original: dict, substitute: dict) -> str:
        orig_score = original.get("nutri_score") or "?"
        sub_score = substitute.get("nutri_score") or "?"
        parts = [
            f"Nutri-Score amélioré : {orig_score} → {sub_score}.",
        ]
        if substitute.get("nova_group") and original.get("nova_group"):
            if substitute["nova_group"] < original["nova_group"]:
                parts.append(
                    f"Niveau NOVA plus faible ({original['nova_group']} → {substitute['nova_group']}), "
                    "donc moins ultra-transformé."
                )
        if original.get("allergens") and not set(substitute.get("allergens", [])).intersection(
            set(original["allergens"])
        ):
            parts.append("Sans les mêmes allergènes que le produit d'origine.")
        return " ".join(parts)

    def _build_description(self, substitute: dict, original: dict) -> str:
        parts = [f"{substitute.get('name', 'Substitut')}"]
        if substitute.get("brand"):
            parts.append(f"de la marque {substitute['brand']}")
        if substitute.get("nutri_score"):
            parts.append(f"(Nutri-Score {substitute['nutri_score']})")
        if substitute.get("ingredients_text"):
            snippet = substitute["ingredients_text"][:200]
            if len(substitute["ingredients_text"]) > 200:
                snippet += "…"
            parts.append(f"Ingrédients : {snippet}")
        elif original.get("category_name"):
            parts.append(f"Alternative dans la catégorie « {original['category_name']} ».")
        return " ".join(parts)

    def _to_response(self, product: dict) -> dict:
        return {
            "barcode": product.get("barcode"),
            "name": product.get("name"),
            "brand": product.get("brand"),
            "category_name": product.get("category_name"),
            "nutri_score": product.get("nutri_score"),
            "nova_group": product.get("nova_group"),
            "allergens": product.get("allergens", []),
            "image_url": product.get("image_url"),
            "off_url": product.get("off_url"),
            "stores": product.get("stores", []),
            "quantity": product.get("quantity"),
        }

    def _product_to_dict(self, product) -> dict:
        return {
            "barcode": product.barcode,
            "name": product.name,
            "brand": product.brand,
            "category_tag": product.category_tag,
            "category_name": product.category_name,
            "nutri_score": product.nutri_score,
            "nova_group": product.nova_group,
            "allergens": product.allergens,
            "ingredients_text": product.ingredients_text,
            "image_url": product.image_url,
            "off_url": product.off_url,
            "stores": product.stores,
            "quantity": product.quantity,
        }
