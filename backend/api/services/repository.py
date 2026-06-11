from datetime import datetime, timedelta
from typing import Any

from django.conf import settings
from pymongo import UpdateOne

from api.models import Category, ProductCache, Substitution
from api.services.data_cleaner import DataCleaner

NUTRI_ORDER = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


class ProductRepository:
    """Enregistre les données nettoyées et effectue les recherches en base."""

    def _product_doc(self, cleaned: dict[str, Any]) -> dict[str, Any]:
        doc = {k: v for k, v in cleaned.items() if k != "raw_data"}
        doc["updated_at"] = datetime.utcnow()
        return doc

    def upsert_product(self, cleaned: dict[str, Any]) -> ProductCache:
        doc = self._product_doc(cleaned)
        barcode = doc.get("barcode")
        product = ProductCache.objects(barcode=barcode).first()
        if product:
            for key, value in doc.items():
                setattr(product, key, value)
            product.save()
            return product

        return ProductCache(**doc).save()

    def upsert_products_bulk(self, cleaned_list: list[dict[str, Any]]) -> list[ProductCache]:
        if not cleaned_list:
            return []

        barcodes: list[str] = []
        operations: list[UpdateOne] = []
        for cleaned in cleaned_list:
            if not cleaned.get("barcode"):
                continue
            doc = self._product_doc(cleaned)
            barcodes.append(doc["barcode"])
            operations.append(
                UpdateOne({"barcode": doc["barcode"]}, {"$set": doc}, upsert=True)
            )

        if not operations:
            return []

        ProductCache._get_collection().bulk_write(operations, ordered=False)
        return list(ProductCache.objects(barcode__in=barcodes))

    def get_product_by_barcode(self, barcode: str) -> ProductCache | None:
        return ProductCache.objects(barcode=barcode.strip()).first()

    def get_products_by_category(self, category_tag: str, limit: int = 50) -> list[ProductCache]:
        return list(
            ProductCache.objects(category_tag=category_tag)
            .order_by("-updated_at")
            .limit(limit)
        )

    def get_fresh_products_by_category(
        self,
        category_tag: str,
        limit: int = 24,
        max_age_hours: int | None = None,
    ) -> list[ProductCache]:
        max_age_hours = max_age_hours or settings.OFF_CACHE_TTL_HOURS
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        return list(
            ProductCache.objects(category_tag=category_tag, updated_at__gte=cutoff)
            .order_by("-updated_at")
            .limit(limit)
        )

    def find_better_in_category_local(
        self,
        category_tag: str,
        max_nutri_score: str,
        exclude_barcode: str | None = None,
        limit: int = 30,
    ) -> list[ProductCache]:
        target = NUTRI_ORDER.get((max_nutri_score or "E").upper(), 5)
        better_grades = [grade for grade, rank in NUTRI_ORDER.items() if rank < target]
        if not better_grades:
            return []

        query = ProductCache.objects(category_tag=category_tag, nutri_score__in=better_grades)
        if exclude_barcode:
            query = query.filter(barcode__ne=exclude_barcode)
        return list(query.order_by("nutri_score").limit(limit))

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
        cleaned_list = []
        for raw in raw_products:
            cleaned = DataCleaner.clean_product(raw)
            if category_tag:
                cleaned["category_tag"] = category_tag
            if cleaned["barcode"]:
                cleaned_list.append(cleaned)
        return self.upsert_products_bulk(cleaned_list)

    @staticmethod
    def product_to_dict(product: ProductCache) -> dict[str, Any]:
        return {
            "barcode": product.barcode,
            "name": product.name,
            "brand": product.brand,
            "category_tag": product.category_tag,
            "category_name": product.category_name,
            "nutri_score": product.nutri_score,
            "ecoscore_grade": product.ecoscore_grade,
            "nova_group": product.nova_group,
            "allergens": product.allergens,
            "ingredients_text": product.ingredients_text,
            "image_url": product.image_url,
            "off_url": product.off_url,
            "stores": product.stores,
            "quantity": product.quantity,
        }
