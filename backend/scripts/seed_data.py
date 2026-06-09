#!/usr/bin/env python
"""
Script d'insertion des données Open Food Facts dans MongoDB.
Usage: python scripts/seed_data.py
"""
import os
import sys
import time

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pur_beurre.settings")
django.setup()

from api.services import OpenFoodFactsClient, ProductRepository  # noqa: E402


def main():
    off = OpenFoodFactsClient()
    repo = ProductRepository()

    print("Insertion des categories populaires...")
    categories = off.get_popular_categories()
    count = repo.seed_categories(categories)
    print(f"  {count} categories enregistrees.")

    print("Telechargement d'echantillons de produits par categorie...")
    total = 0
    for cat in categories:
        products = off.search_products_by_category(cat["tag"], page_size=15)
        cached = repo.cache_products_from_raw(products)
        total += len(cached)
        print(f"  [{cat['name_fr']}] {len(cached)} produits mis en cache.")
        time.sleep(1)

    print(f"\nTermine : {total} produits inseres/mis a jour en base.")


if __name__ == "__main__":
    main()
