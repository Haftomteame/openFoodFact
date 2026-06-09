from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import create_jwt_token, hash_password, verify_password
from api.models import User
from api.serializers import (
    BarcodeSerializer,
    CategoryProductsSerializer,
    LoginSerializer,
    RegisterSerializer,
    SaveSubstitutionSerializer,
    SearchProductsSerializer,
    SubstituteRequestSerializer,
    UserAllergensSerializer,
)
from api.services import (
    DataCleaner,
    OpenFoodFactsClient,
    ProductRepository,
    SubstituteFinder,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if User.objects(email=data["email"]).first():
            return Response(
                {"error": "Un compte existe déjà avec cet e-mail."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User(
            email=data["email"],
            password_hash=hash_password(data["password"]),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
        ).save()

        token = create_jwt_token(user)
        return Response(
            {
                "token": token,
                "user": _user_response(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects(email=data["email"]).first()
        if not user or not verify_password(data["password"], user.password_hash):
            return Response(
                {"error": "E-mail ou mot de passe incorrect."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = create_jwt_token(user)
        return Response(
            {
                "token": token,
                "user": _user_response(user),
            }
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_user_response(request.user))

    def patch(self, request):
        serializer = UserAllergensSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.allergens = serializer.validated_data["allergens"]
        request.user.save()
        return Response(_user_response(request.user))


class AllergensView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from api.allergens import COMMON_ALLERGENS

        return Response(
            [{"key": a["key"], "label_fr": a["label_fr"]} for a in COMMON_ALLERGENS]
        )


class CategoriesView(APIView):
    def get(self, request):
        repo = ProductRepository()
        categories = repo.list_categories()
        if not categories:
            off = OpenFoodFactsClient()
            repo.seed_categories(off.get_popular_categories())
            categories = repo.list_categories()

        return Response(
            [
                {
                    "tag": c.tag,
                    "name_fr": c.name_fr,
                    "name_en": c.name_en,
                }
                for c in categories
            ]
        )


class CategoryProductsView(APIView):
    def get(self, request):
        serializer = CategoryProductsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        off = OpenFoodFactsClient()
        repo = ProductRepository()

        category_tag = data["category_tag"]
        page_size = data.get("page_size", 24)

        raw_products = off.search_products_by_category(
            category_tag=category_tag,
            page_size=page_size,
            page=data.get("page", 1),
        )
        products = repo.cache_products_from_raw(raw_products, category_tag=category_tag)

        return Response(
            {
                "category_tag": category_tag,
                "count": len(products),
                "products": [_product_response(p) for p in products],
            }
        )


class SearchProductsView(APIView):
    def get(self, request):
        serializer = SearchProductsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        off = OpenFoodFactsClient()
        repo = ProductRepository()

        raw_products = off.search_products_by_name(
            query=data["q"],
            page_size=data.get("page_size", 24),
        )
        products = repo.cache_products_from_raw(raw_products)

        return Response(
            {
                "query": data["q"],
                "count": len(products),
                "products": [_product_response(p) for p in products],
            }
        )


class ProductByBarcodeView(APIView):
    def get(self, request, barcode):
        serializer = BarcodeSerializer(data={"barcode": barcode})
        serializer.is_valid(raise_exception=True)
        barcode = serializer.validated_data["barcode"]

        repo = ProductRepository()
        product = repo.get_product_by_barcode(barcode)

        if not product:
            off = OpenFoodFactsClient()
            raw = off.get_product_by_barcode(barcode)
            if not raw:
                return Response(
                    {"error": "Produit non trouvé sur Open Food Facts."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            cleaned = DataCleaner.clean_product(raw)
            product = repo.upsert_product(cleaned)

        return Response(_product_response(product))


class SubstituteView(APIView):
    def post(self, request):
        serializer = SubstituteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        finder = SubstituteFinder()
        user_allergens = data.get("user_allergens") or []
        if (
            hasattr(request, "user")
            and request.user
            and getattr(request.user, "is_authenticated", False)
            and not getattr(request.user, "is_anonymous", True)
        ):
            if not user_allergens:
                user_allergens = getattr(request.user, "allergens", None) or []

        result = finder.find_substitute(
            barcode=data.get("barcode"),
            avoid_allergens=data.get("avoid_allergens", True),
            user_allergens=user_allergens,
        )

        if not result.get("success"):
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class SaveSubstitutionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SaveSubstitutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        repo = ProductRepository()
        original = repo.get_product_by_barcode(data["original_barcode"])
        substitute = repo.get_product_by_barcode(data["substitute_barcode"])

        if not original or not substitute:
            return Response(
                {"error": "Produit original ou substitut introuvable en base."},
                status=status.HTTP_404_NOT_FOUND,
            )

        finder = SubstituteFinder()
        user_allergens = getattr(request.user, "allergens", None) or []
        reason = data.get("reason") or finder._build_reason(
            _product_dict(original),
            _product_dict(substitute),
            user_allergens,
        )

        sub = repo.save_substitution(
            user_id=str(request.user.id),
            original=_product_dict(original),
            substitute={
                **_product_dict(substitute),
                "description": finder._build_description(
                    _product_dict(substitute),
                    _product_dict(original),
                ),
            },
            reason=reason,
        )

        return Response(_substitution_response(sub), status=status.HTTP_201_CREATED)


class MySubstitutionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        repo = ProductRepository()
        subs = repo.get_user_substitutions(str(request.user.id))
        return Response([_substitution_response(s) for s in subs])


class DeleteSubstitutionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, substitution_id):
        repo = ProductRepository()
        deleted = repo.delete_substitution(str(request.user.id), substitution_id)
        if not deleted:
            return Response(
                {"error": "Substitution introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"})


def _user_response(user) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "allergens": getattr(user, "allergens", None) or [],
    }


def _product_dict(product) -> dict:
    return {
        "barcode": product.barcode,
        "name": product.name,
        "brand": product.brand,
        "category_name": product.category_name,
        "category_tag": product.category_tag,
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


def _product_response(product) -> dict:
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


def _substitution_response(sub) -> dict:
    return {
        "id": str(sub.id),
        "original_barcode": sub.original_barcode,
        "original_name": sub.original_name,
        "substitute_barcode": sub.substitute_barcode,
        "substitute_name": sub.substitute_name,
        "substitute_description": sub.substitute_description,
        "substitute_stores": sub.substitute_stores,
        "substitute_off_url": sub.substitute_off_url,
        "substitute_nutri_score": sub.substitute_nutri_score,
        "original_nutri_score": getattr(sub, "original_nutri_score", None),
        "reason": sub.reason,
        "saved_at": sub.saved_at.isoformat() if sub.saved_at else None,
    }
