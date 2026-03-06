from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from portal.models import Article, Brand, Category, ErrorCode


class PortalViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.news = Category.objects.create(
            name="Новини",
            name_ru="Новости",
            name_en="News",
            slug="news",
            description="Украинское описание",
            description_ru="Русское описание",
            description_en="English description",
            position=1,
            seo_title="Новини",
            seo_title_ru="Новости",
            seo_title_en="News",
            meta_description="Мета укр",
            meta_description_ru="Мета ру",
            meta_description_en="Meta en",
        )
        cls.errors = Category.objects.create(
            name="Помилки",
            name_ru="Ошибки",
            name_en="Errors",
            slug="errors",
            description="Опис помилок",
            description_ru="Описание ошибок",
            description_en="Error description",
            position=5,
            seo_title="Помилки",
            seo_title_ru="Ошибки",
            seo_title_en="Errors",
            meta_description="Мета укр",
            meta_description_ru="Мета ру",
            meta_description_en="Meta en",
        )
        cls.brand = Brand.objects.create(
            name="ЛДЖИ",
            name_ru="ЛЖ",
            name_en="LG",
            slug="lg",
            description="Опис бренду",
            description_ru="Описание бренда",
            description_en="Brand description",
            seo_title="ЛДЖИ",
            seo_title_ru="ЛЖ",
            seo_title_en="LG",
            meta_description="Мета укр",
            meta_description_ru="Мета ру",
            meta_description_en="Meta en",
        )
        cls.article = Article.objects.create(
            title="Найкращі пральні машини 2026",
            title_ru="Лучшие стиральные машины 2026",
            title_en="Best Washing Machines 2026",
            slug="best-washing-machines-2026",
            excerpt="Український анонс",
            excerpt_ru="Русский анонс",
            excerpt_en="English excerpt",
            content="Абзац один.\n\nАбзац два.\n\nАбзац три.",
            content_ru="Абзац один.\n\nАбзац два.\n\nАбзац три.",
            content_en="Paragraph one.\n\nParagraph two.\n\nParagraph three.",
            category=cls.news,
            brand=cls.brand,
            seo_title="SEO укр",
            seo_title_ru="SEO ру",
            seo_title_en="SEO en",
            meta_description="Мета укр",
            meta_description_ru="Мета ру",
            meta_description_en="Meta en",
            featured=True,
        )
        cls.error = ErrorCode.objects.create(
            brand=cls.brand,
            code="OE",
            title="Помилка LG OE",
            title_ru="Ошибка LG OE",
            title_en="LG OE error explained",
            slug="lg-oe-error",
            description="Український опис",
            description_ru="Русское описание",
            description_en="Drainage issue detected.",
            causes="Українські причини",
            causes_ru="Русские причины",
            causes_en="Clogged filter.",
            solutions="Українське рішення",
            solutions_ru="Русское решение",
            solutions_en="Clean the drain pump filter and inspect the hose.",
            seo_title="SEO укр",
            seo_title_ru="SEO ру",
            seo_title_en="SEO en",
            meta_description="Мета укр",
            meta_description_ru="Мета ру",
            meta_description_en="Meta en",
        )

    def test_home_page_loads(self):
        with translation.override("en"):
            response = self.client.get(reverse("portal:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Best Washing Machines 2026")

    def test_root_redirects_to_default_ukrainian_prefix(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/uk/")

    def test_article_detail_increments_views(self):
        with translation.override("en"):
            response = self.client.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.views, 1)

    def test_search_returns_article_and_error_code(self):
        with translation.override("en"):
            response = self.client.get(reverse("portal:search"), {"q": "LG"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Best Washing Machines 2026")
        self.assertContains(response, "LG OE error explained")

    def test_sitemap_contains_article_url(self):
        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/uk/news/best-washing-machines-2026")
