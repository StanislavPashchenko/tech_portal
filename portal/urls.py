from django.urls import path

from portal import views

app_name = "portal"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("categories/", views.CategoryIndexView.as_view(), name="category_index"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("brands/", views.BrandListView.as_view(), name="brand_list"),
    path("brands/<slug:slug>", views.BrandDetailView.as_view(), name="brand_detail"),
    path(
        "news/",
        views.CategoryArticleListView.as_view(),
        {"category_slug": "news"},
        name="news_list",
    ),
    path(
        "reviews/",
        views.CategoryArticleListView.as_view(),
        {"category_slug": "reviews"},
        name="reviews_list",
    ),
    path(
        "comparisons/",
        views.CategoryArticleListView.as_view(),
        {"category_slug": "comparisons"},
        name="comparisons_list",
    ),
    path(
        "guides/",
        views.CategoryArticleListView.as_view(),
        {"category_slug": "guides"},
        name="guides_list",
    ),
    path("errors/", views.ErrorCodeListView.as_view(), name="error_list"),
    path("errors/<slug:slug>", views.ErrorCodeDetailView.as_view(), name="error_detail"),
    path(
        "<slug:category_slug>/<slug:slug>",
        views.ArticleDetailView.as_view(),
        name="article_detail",
    ),
]
