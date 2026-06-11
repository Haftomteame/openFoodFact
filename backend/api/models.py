from datetime import datetime

from mongoengine import (
    DateTimeField,
    DictField,
    Document,
    EmailField,
    IntField,
    ListField,
    StringField,
)


class User(Document):
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    first_name = StringField(max_length=100)
    last_name = StringField(max_length=100)
    allergens = ListField(StringField(), default=list)
    created_at = DateTimeField(default=datetime.utcnow)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    meta = {"collection": "users", "indexes": ["email"]}


class Category(Document):
    tag = StringField(required=True, unique=True)
    name_fr = StringField(required=True)
    name_en = StringField()
    product_count = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "categories", "indexes": ["tag", "name_fr"]}


class ProductCache(Document):
    barcode = StringField(required=True, unique=True)
    name = StringField(required=True)
    brand = StringField()
    category_tag = StringField()
    category_name = StringField()
    nutri_score = StringField()
    ecoscore_grade = StringField()
    nova_group = IntField()
    allergens = ListField(StringField())
    ingredients_text = StringField()
    image_url = StringField()
    off_url = StringField()
    stores = ListField(StringField())
    countries = ListField(StringField())
    quantity = StringField()
    raw_data = DictField()
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "products_cache",
        "indexes": [
            "barcode",
            "category_tag",
            "name",
            "nutri_score",
            ("category_tag", "nutri_score"),
            ("category_tag", "-updated_at"),
        ],
    }


class Substitution(Document):
    user_id = StringField(required=True)
    original_barcode = StringField(required=True)
    original_name = StringField(required=True)
    substitute_barcode = StringField(required=True)
    substitute_name = StringField(required=True)
    substitute_description = StringField()
    substitute_stores = ListField(StringField())
    substitute_off_url = StringField()
    substitute_nutri_score = StringField()
    original_nutri_score = StringField()
    reason = StringField()
    saved_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "substitutions",
        "indexes": ["user_id", ("user_id", "-saved_at")],
    }
