from django.urls import path

from portal import views

app_name = "portal"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("items/", views.ProductListView.as_view(), name="product_list"),
    path("items/type/<slug:type_slug>/", views.ProductApplianceTypeListView.as_view(), name="product_type"),
    path(
        "items/type/<slug:type_slug>/brands/<slug:brand_slug>/",
        views.ProductBrandListView.as_view(),
        name="product_brand",
    ),
    path(
        "items/type/<slug:type_slug>/<slug:brand_slug>/<slug:slug>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    path("articles/", views.ArticleListView.as_view(), name="article_list"),
    path("articles/<slug:slug>", views.ArticleDetailView.as_view(), name="article_detail"),
    path("errors/", views.ErrorApplianceTypeListView.as_view(), name="error_list"),
    path("errors/<slug:type_slug>/", views.ErrorBrandListView.as_view(), name="error_type"),
    path(
        "errors/<slug:type_slug>/<slug:brand_slug>/",
        views.ErrorModelListView.as_view(),
        name="error_brand",
    ),
    path(
        "errors/<slug:type_slug>/<slug:brand_slug>/<slug:model_slug>/",
        views.ErrorCodeListView.as_view(),
        name="error_model",
    ),
    path(
        "errors/<slug:type_slug>/<slug:brand_slug>/<slug:model_slug>/<slug:slug>/",
        views.ErrorCodeDetailView.as_view(),
        name="error_detail",
    ),
]
