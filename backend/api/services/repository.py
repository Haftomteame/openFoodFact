from typing import Any

from api.models import Category, ProductCache, Substitution
from api.services.data_cleaner import DataCleaner


class ProductRepository:
    """Enregistre les données nettoyées et effectue les recherches en base."""

    def upsert_product(self, cleaned: dict[str, Any]) -> ProductCache:
        product = ProductCache.objects(barcode=cleaned["barcode"]).first()
        if product:
            for key, value in cleaned.items():
                if key != "raw_data":
                    setattr(product, key, value)
            product.save()
            return product

        return ProductCache(**cleaned).save()

    def get_product_by_barcode(self, barcode: str) -> ProductCache | None:
        return ProductCache.objects(barcode=barcode.strip()).first()

    def get_products_by_category(self, category_tag: str, limit: int = 50) -> list[ProductCache]:
        return list(
            ProductCache.objects(category_tag=category_tag)
            .order_by("-updated_at")
            .limit(limit)
        )

    def search_products_local(self, query: str, limit: int = 20) -> list[ProductCache]:
        return list(
            ProductCache.objects(name__icontains=query.strip())
            .order_by("-updated_at")
            .limit(limit)
        )

    def seed_categories(self, categories: list[dict[str, str]]) -> int:
        count = 0
        for cat in categories:
            existing = Category.objects(tag=cat["tag"]).first()
            if existing:
                existing.name_fr = cat["name_fr"]
                existing.name_en = cat.get("name_en", "")
                existing.save()
            else:
                Category(
                    tag=cat["tag"],
                    name_fr=cat["name_fr"],
                    name_en=cat.get("name_en", ""),
                ).save()
            count += 1
        return count

    def list_categories(self) -> list[Category]:
        return list(Category.objects.order_by("name_fr"))

    def save_substitution(
        self,
        user_id: str,
        original: dict[str, Any],
        substitute: dict[str, Any],
        reason: str,
    ) -> Substitution:
        return Substitution(
            user_id=user_id,
            original_barcode=original["barcode"],
            original_name=original["name"],
            substitute_barcode=substitute["barcode"],
            substitute_name=substitute["name"],
            substitute_description=substitute.get("description", ""),
            substitute_stores=substitute.get("stores", []),
            substitute_off_url=substitute.get("off_url", ""),
            substitute_nutri_score=substitute.get("nutri_score"),
            original_nutri_score=original.get("nutri_score"),
            reason=reason,
        ).save()

    def get_user_substitutions(self, user_id: str) -> list[Substitution]:
        return list(Substitution.objects(user_id=user_id).order_by("-saved_at"))

    def delete_substitution(self, user_id: str, substitution_id: str) -> bool:
        sub = Substitution.objects(id=substitution_id, user_id=user_id).first()
        if sub:
            sub.delete()
            return True
        return False

    def cache_products_from_raw(
        self,
        raw_products: list[dict],
        category_tag: str | None = None,
    ) -> list[ProductCache]:
        cached = []
        for raw in raw_products:
            cleaned = DataCleaner.clean_product(raw)
            if category_tag:
                cleaned["category_tag"] = category_tag
            if cleaned["barcode"]:
                cached.append(self.upsert_product(cleaned))
        return cached
