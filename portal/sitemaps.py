from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import translation

from portal.models import Article, Brand, Category, ErrorCode


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
        return ErrorCode.objects.select_related("brand")

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
                    (language, "portal:category_index"),
                    (language, "portal:brand_list"),
                ]
            )
        return pages

    def location(self, item):
        language, view_name = item
        with translation.override(language):
            return reverse(view_name)


class BrandSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return [
            (language, brand)
            for language, _ in settings.LANGUAGES
            for brand in Brand.objects.all()
        ]

    def location(self, item):
        language, brand = item
        with translation.override(language):
            return brand.get_absolute_url()

    def lastmod(self, item):
        return item[1].updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return [
            (language, category)
            for language, _ in settings.LANGUAGES
            for category in Category.objects.all()
        ]

    def location(self, item):
        language, category = item
        with translation.override(language):
            return category.get_absolute_url()

    def lastmod(self, item):
        return item[1].updated_at


sitemaps = {
    "static": LocalizedStaticViewSitemap,
    "categories": CategorySitemap,
    "brands": BrandSitemap,
    "articles": ArticleSitemap,
    "errors": ErrorCodeSitemap,
}
