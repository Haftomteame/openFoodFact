from django.urls import path

from api.views import (
    AllergensView,
    CategoriesView,
    CategoryProductsView,
    DeleteSubstitutionView,
    HealthView,
    LoginView,
    MeView,
    MySubstitutionsView,
    ProductByBarcodeView,
    RegisterView,
    SaveSubstitutionView,
    SearchProductsView,
    SubstituteView,
)

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("allergens/", AllergensView.as_view(), name="allergens"),
    path("categories/", CategoriesView.as_view(), name="categories"),
    path("categories/products/", CategoryProductsView.as_view(), name="category-products"),
    path("search/", SearchProductsView.as_view(), name="search-products"),
    path("products/<str:barcode>/", ProductByBarcodeView.as_view(), name="product-barcode"),
    path("substitute/", SubstituteView.as_view(), name="substitute"),
    path("substitutions/save/", SaveSubstitutionView.as_view(), name="save-substitution"),
    path("substitutions/", MySubstitutionsView.as_view(), name="my-substitutions"),
    path(
        "substitutions/<str:substitution_id>/",
        DeleteSubstitutionView.as_view(),
        name="delete-substitution",
    ),
]
