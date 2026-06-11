import logging
import time
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

LIST_FIELDS = (
    "code,product_name,brands,categories,categories_tags,categories_tags_fr,"
    "nutrition_grades,nutriscore_grade,nova_group,ecoscore_grade,"
    "allergens_tags,image_front_url,image_url,stores,purchase_places,quantity,url"
)

DETAIL_FIELDS = (
    f"{LIST_FIELDS},ingredients_text_fr,ingredients_text,ecoscore_score,"
    "countries_tags,product_quantity"
)

_off_client: "OpenFoodFactsClient | None" = None


def get_off_client() -> "OpenFoodFactsClient":
    global _off_client
    if _off_client is None:
        _off_client = OpenFoodFactsClient()
    return _off_client


class OpenFoodFactsClient:
    """Télécharge les données depuis l'API Open Food Facts."""

    def __init__(self, base_url: str | None = None, timeout: int = 15, max_retries: int = 2):
        self.base_url = (base_url or settings.OFF_API_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "FoodFactsHub/1.0 (IPSSI - Open Food Facts Project)",
                "Accept": "application/json",
            }
        )

    def _get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                if response.status_code in (429, 503) and attempt < self.max_retries - 1:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                if attempt < self.max_retries - 1:
                    time.sleep(1.0 * (attempt + 1))
        raise last_error  # type: ignore[misc]

    def get_product_by_barcode(self, barcode: str) -> dict[str, Any] | None:
        barcode = barcode.strip()
        if not barcode.isdigit() or len(barcode) < 8:
            return None
        try:
            data = self._get(f"/api/v2/product/{barcode}", params={"fields": DETAIL_FIELDS})
            if data.get("status") == 1 and data.get("product"):
                return data["product"]
        except requests.RequestException as exc:
            logger.warning("Erreur OFF produit %s: %s", barcode, exc)
        return None

    def search_products_by_category(
        self,
        category_tag: str,
        page_size: int = 24,
        page: int = 1,
        countries: str = "france",
    ) -> list[dict[str, Any]]:
        try:
            data = self._get(
                "/api/v2/search",
                params={
                    "categories_tags": category_tag,
                    "countries_tags": countries,
                    "page_size": page_size,
                    "page": page,
                    "fields": LIST_FIELDS,
                    "sort_by": "popularity_key",
                },
            )
            products = data.get("products", [])
            if products:
                return products
        except requests.RequestException as exc:
            logger.warning("Erreur OFF v2 recherche categorie %s: %s", category_tag, exc)

        return self._search_category_legacy(category_tag, page_size, page)

    def _search_category_legacy(
        self,
        category_tag: str,
        page_size: int,
        page: int,
    ) -> list[dict[str, Any]]:
        tag_label = category_tag.replace("en:", "").replace("-", " ")
        try:
            data = self._get(
                "/cgi/search.pl",
                params={
                    "action": "process",
                    "tagtype_0": "categories",
                    "tag_contains_0": "contains",
                    "tag_0": tag_label,
                    "json": 1,
                    "page_size": page_size,
                    "page": page,
                    "fields": LIST_FIELDS,
                    "countries": "France",
                },
            )
            return data.get("products", [])
        except requests.RequestException as exc:
            logger.warning("Erreur OFF legacy recherche categorie %s: %s", category_tag, exc)
            return []

    def search_products_by_name(
        self,
        query: str,
        page_size: int = 24,
        countries: str = "france",
    ) -> list[dict[str, Any]]:
        try:
            data = self._get(
                "/cgi/search.pl",
                params={
                    "search_terms": query,
                    "search_simple": 1,
                    "action": "process",
                    "json": 1,
                    "page_size": page_size,
                    "countries_tags": countries,
                    "fields": LIST_FIELDS,
                },
            )
            return data.get("products", [])
        except requests.RequestException as exc:
            logger.warning("Erreur OFF recherche texte %s: %s", query, exc)
            return []

    def find_better_in_category(
        self,
        category_tag: str,
        max_nutri_score: str,
        exclude_barcode: str | None = None,
        limit: int = 30,
    ) -> list[dict[str, Any]]:
        nutri_order = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        target = nutri_order.get(max_nutri_score.lower(), 5)
        better_grades = [g for g, v in nutri_order.items() if v < target]

        candidates: list[dict[str, Any]] = []
        page_size = min(limit, 20)

        for grade in better_grades:
            try:
                data = self._get(
                    "/api/v2/search",
                    params={
                        "categories_tags": category_tag,
                        "nutrition_grades_tags": grade,
                        "countries_tags": "france",
                        "page_size": page_size,
                        "fields": LIST_FIELDS,
                        "sort_by": "popularity_key",
                    },
                )
                candidates.extend(data.get("products", []))
            except requests.RequestException:
                continue

            if len(candidates) >= limit:
                break

        if exclude_barcode:
            candidates = [p for p in candidates if p.get("code") != exclude_barcode]
        return candidates[:limit]

    def get_popular_categories(self) -> list[dict[str, str]]:
        return [
            {"tag": "en:chocolate-spreads", "name_fr": "Pâtes à tartiner"},
            {"tag": "en:biscuits", "name_fr": "Biscuits et gâteaux"},
            {"tag": "en:sodas", "name_fr": "Sodas et boissons sucrées"},
            {"tag": "en:chips", "name_fr": "Chips et snacks salés"},
            {"tag": "en:ice-creams", "name_fr": "Glaces et sorbets"},
            {"tag": "en:breakfast-cereals", "name_fr": "Céréales petit-déjeuner"},
            {"tag": "en:plant-based-spreads", "name_fr": "Pâtes végétales"},
            {"tag": "en:yogurts", "name_fr": "Yaourts"},
            {"tag": "en:fruit-juices", "name_fr": "Jus de fruits"},
            {"tag": "en:ready-meals", "name_fr": "Plats préparés"},
            {"tag": "en:frozen-pizzas", "name_fr": "Pizzas surgelées"},
            {"tag": "en:cheeses", "name_fr": "Fromages"},
        ]
