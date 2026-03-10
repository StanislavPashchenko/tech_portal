from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import translation

from portal.models import Article, CatalogItem, ErrorCode


class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Article.objects.published().select_related("category")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class ErrorCodeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ErrorCode.objects.select_related(
            "repair_model",
            "repair_model__repair_brand",
            "repair_model__repair_brand__appliance_type",
        )

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CatalogItemSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.85

    def items(self):
        return CatalogItem.objects.select_related(
            "repair_model",
            "repair_model__repair_brand",
            "repair_model__repair_brand__appliance_type",
        )

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class LocalizedStaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        pages = []
        for language, _ in settings.LANGUAGES:
            pages.extend(
                [
                    (language, "portal:home"),
                    (language, "portal:error_list"),
                    (language, "portal:product_list"),
                ]
            )
        return pages

    def location(self, item):
        language, view_name = item
        with translation.override(language):
            return reverse(view_name)


sitemaps = {
    "static": LocalizedStaticViewSitemap,
    "articles": ArticleSitemap,
    "products": CatalogItemSitemap,
    "errors": ErrorCodeSitemap,
}
