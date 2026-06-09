import re

from rest_framework import serializers


EMAIL_REGEX = re.compile(r"^[\w.\-+]+@[\w.\-]+\.\w+$")
BARCODE_REGEX = re.compile(r"^\d{8,14}$")


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_email(self, value):
        if not EMAIL_REGEX.match(value):
            raise serializers.ValidationError("Adresse e-mail invalide.")
        return value.lower().strip()

    def validate_password(self, value):
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Le mot de passe doit contenir au moins une lettre et un chiffre."
            )
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.lower().strip()


class BarcodeSerializer(serializers.Serializer):
    barcode = serializers.CharField()

    def validate_barcode(self, value):
        cleaned = value.strip().replace(" ", "")
        if not BARCODE_REGEX.match(cleaned):
            raise serializers.ValidationError(
                "Code-barres invalide (8 à 14 chiffres attendus)."
            )
        return cleaned


class SearchProductsSerializer(serializers.Serializer):
    q = serializers.CharField(min_length=2)
    page_size = serializers.IntegerField(min_value=1, max_value=50, default=24, required=False)


class CategoryProductsSerializer(serializers.Serializer):
    category_tag = serializers.CharField()
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(min_value=1, max_value=50, default=24, required=False)


class SubstituteRequestSerializer(serializers.Serializer):
    barcode = serializers.CharField(required=False, allow_blank=True)
    avoid_allergens = serializers.BooleanField(default=True, required=False)

    def validate_barcode(self, value):
        if not value:
            return value
        cleaned = value.strip().replace(" ", "")
        if not BARCODE_REGEX.match(cleaned):
            raise serializers.ValidationError("Code-barres invalide.")
        return cleaned


class SaveSubstitutionSerializer(serializers.Serializer):
    original_barcode = serializers.CharField()
    substitute_barcode = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True)
