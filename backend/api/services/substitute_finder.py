from typing import Any

from django.conf import settings

from api.allergens import product_has_allergens
from api.services.data_cleaner import DataCleaner
from api.services.off_client import OpenFoodFactsClient, get_off_client
from api.services.repository import ProductRepository

NUTRI_RANK = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


class SubstituteFinder:
    """Propose un substitut plus sain pour un produit donné."""

    def __init__(
        self,
        off_client: OpenFoodFactsClient | None = None,
        repository: ProductRepository | None = None,
    ):
        self.off_client = off_client or get_off_client()
        self.repository = repository or ProductRepository()

    def find_substitute(
        self,
        barcode: str | None = None,
        product_data: dict[str, Any] | None = None,
        avoid_allergens: bool = True,
        user_allergens: list[str] | None = None,
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

        max_nutri = original.get("nutri_score") or "E"
        exclude_barcode = original.get("barcode")

        local_products = self.repository.find_better_in_category_local(
            category_tag=category_tag,
            max_nutri_score=max_nutri,
            exclude_barcode=exclude_barcode,
        )
        min_local = settings.SUBSTITUTE_LOCAL_MIN_CANDIDATES

        if len(local_products) >= min_local:
            cleaned_candidates = [
                self.repository.product_to_dict(product) for product in local_products
            ]
        else:
            candidates_raw = self.off_client.find_better_in_category(
                category_tag=category_tag,
                max_nutri_score=max_nutri,
                exclude_barcode=exclude_barcode,
            )

            if not candidates_raw:
                candidates_raw = self.off_client.search_products_by_category(
                    category_tag=category_tag,
                    page_size=30,
                )
                candidates_raw = [
                    p for p in candidates_raw if p.get("code") != exclude_barcode
                ]

            cleaned_candidates = [DataCleaner.clean_product(p) for p in candidates_raw]
            cleaned_candidates = [c for c in cleaned_candidates if c["barcode"]]

            if local_products:
                seen = {c["barcode"] for c in cleaned_candidates}
                for product in local_products:
                    if product.barcode not in seen:
                        cleaned_candidates.append(self.repository.product_to_dict(product))
                        seen.add(product.barcode)

        if len(cleaned_candidates) < min_local:
            seen = {c["barcode"] for c in cleaned_candidates}
            for product in self.repository.get_products_by_category(category_tag, limit=30):
                if product.barcode == exclude_barcode or product.barcode in seen:
                    continue
                cleaned_candidates.append(self.repository.product_to_dict(product))
                seen.add(product.barcode)

        forbidden_keys = list(user_allergens or [])
        if avoid_allergens and forbidden_keys:
            safe_candidates = [
                c
                for c in cleaned_candidates
                if not product_has_allergens(c.get("allergens", []), forbidden_keys)
            ]
            if safe_candidates:
                cleaned_candidates = safe_candidates

        substitute = self._pick_best(cleaned_candidates, original)
        if not substitute:
            msg = "Aucun substitut plus sain trouvé dans cette catégorie."
            if forbidden_keys and avoid_allergens:
                msg = (
                    "Aucun substitut plus sain trouvé sans vos allergènes "
                    "déclarés dans cette catégorie."
                )
            return {
                "success": False,
                "error": msg,
                "original": self._to_response(original),
            }

        top_candidates = self._pick_top(cleaned_candidates, original, limit=3)
        alternative_barcodes = {substitute["barcode"]}
        alternatives = []
        for candidate in top_candidates:
            if candidate["barcode"] in alternative_barcodes:
                continue
            alternative_barcodes.add(candidate["barcode"])
            alternatives.append(
                {
                    **self._to_response(candidate),
                    "description": self._build_description(candidate, original),
                }
            )
            if len(alternatives) >= 2:
                break

        self.repository.upsert_products_bulk([original, substitute, *top_candidates])

        reason = self._build_reason(original, substitute, forbidden_keys if avoid_allergens else [])

        return {
            "success": True,
            "original": self._to_response(original),
            "substitute": {
                **self._to_response(substitute),
                "description": self._build_description(substitute, original),
            },
            "reason": reason,
            "allergy_safe": bool(
                forbidden_keys
                and not product_has_allergens(substitute.get("allergens", []), forbidden_keys)
            ),
            "alternatives": alternatives,
            "improvement": self._compute_improvement(original, substitute),
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
            return self.repository.product_to_dict(cached)

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

    def _pick_top(
        self,
        candidates: list[dict[str, Any]],
        original: dict[str, Any],
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        if not candidates:
            return []

        original_rank = NUTRI_RANK.get(original.get("nutri_score") or "E", 5)

        def score(candidate: dict[str, Any]) -> tuple:
            nutri = NUTRI_RANK.get(candidate.get("nutri_score") or "E", 5)
            has_stores = 0 if candidate.get("stores") else 1
            has_image = 0 if candidate.get("image_url") else 1
            return (nutri, has_stores, has_image)

        better = [c for c in candidates if score(c)[0] < original_rank]
        pool = better if better else candidates
        return sorted(pool, key=score)[:limit]

    def _compute_improvement(self, original: dict, substitute: dict) -> dict:
        orig_rank = NUTRI_RANK.get((original.get("nutri_score") or "E").upper(), 5)
        sub_rank = NUTRI_RANK.get((substitute.get("nutri_score") or "E").upper(), 5)
        nova_delta = None
        if original.get("nova_group") and substitute.get("nova_group"):
            nova_delta = original["nova_group"] - substitute["nova_group"]
        return {
            "nutri_score_before": original.get("nutri_score"),
            "nutri_score_after": substitute.get("nutri_score"),
            "nutri_steps": max(0, orig_rank - sub_rank),
            "nova_delta": nova_delta,
        }

    def _build_reason(self, original: dict, substitute: dict, user_allergens: list[str]) -> str:
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
        if user_allergens and not product_has_allergens(
            substitute.get("allergens", []), user_allergens
        ):
            parts.append("Compatible avec vos allergènes déclarés.")
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
            "category_tag": product.get("category_tag"),
            "nutri_score": product.get("nutri_score"),
            "ecoscore_grade": product.get("ecoscore_grade"),
            "nova_group": product.get("nova_group"),
            "allergens": product.get("allergens", []),
            "ingredients_text": product.get("ingredients_text"),
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
