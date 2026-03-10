from django.test import TestCase
from django.core.management import call_command
from django.urls import reverse
from django.utils import translation

from portal.models import (
    Article,
    Brand,
    CatalogItem,
    CatalogItemFault,
    CatalogItemImage,
    Category,
    ErrorCode,
    RepairApplianceType,
    RepairBrand,
    RepairModel,
)


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
        cls.brand = Brand.objects.create(
            name="ЛДЖИ",
            name_ru="ЛЖ",
            name_en="LG",
            slug="lg",
            description="Описание бренда",
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
            excerpt="Украинский анонс",
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
        cls.appliance_type = RepairApplianceType.objects.create(
            name="Пральні машини",
            name_ru="Стиральные машины",
            name_en="Washing Machines",
            slug="washing-machines",
        )
        cls.repair_brand = RepairBrand.objects.create(
            appliance_type=cls.appliance_type,
            name="LG",
            name_ru="LG",
            name_en="LG",
            slug="lg-repair",
        )
        cls.repair_model = RepairModel.objects.create(
            repair_brand=cls.repair_brand,
            name="LG F2J6WS0W",
            name_ru="LG F2J6WS0W",
            name_en="LG F2J6WS0W",
            slug="lg-f2j6ws0w",
        )
        cls.error = ErrorCode.objects.create(
            repair_model=cls.repair_model,
            code="OE",
            title="Помилка LG OE",
            title_ru="Ошибка LG OE",
            title_en="LG OE error explained",
            slug="lg-oe-error",
            description="Украинское описание",
            description_ru="Русское описание",
            description_en="Drainage issue detected.",
            causes="Украинские причины",
            causes_ru="Русские причины",
            causes_en="Clogged filter.",
            solutions="Украинское решение",
            solutions_ru="Русское решение",
            solutions_en="Clean the drain pump filter and inspect the hose.",
            seo_title="SEO укр",
            seo_title_ru="SEO ру",
            seo_title_en="SEO en",
            meta_description="Мета укр",
            meta_description_ru="Мета ру",
            meta_description_en="Meta en",
        )
        cls.catalog_item = CatalogItem.objects.create(
            repair_model=cls.repair_model,
            source_url="https://example.com/lg-f2j6ws0w",
            product_description="Detailed washer page with repair data.",
            primary_image="/media/catalog/lg-f2j6ws0w/image-01.jpg",
            coverage="brand-generic repair data plus model-specific search URLs",
            short_specs={"Load": "6 kg", "Spin": "1200 rpm"},
            repair_tips=["Clean the filter first."],
            notes=["Check the exact service manual for this model."],
            model_search_urls={"manual_search": "https://example.com/manual"},
            source_links=[{"title": "Service Manual", "url": "https://example.com/source"}],
            seo_title="LG F2J6WS0W",
            seo_title_ru="LG F2J6WS0W",
            seo_title_en="LG F2J6WS0W",
            meta_description="Catalog item meta",
            meta_description_ru="Catalog item meta",
            meta_description_en="Catalog item meta",
        )
        cls.refrigerator_type = RepairApplianceType.objects.create(
            name="Холодильники",
            name_ru="Холодильники",
            name_en="Refrigerators",
            slug="refrigerators",
        )
        cls.refrigerator_brand = RepairBrand.objects.create(
            appliance_type=cls.refrigerator_type,
            name="AEG",
            name_ru="AEG",
            name_en="AEG",
            slug="aeg-repair",
        )
        cls.refrigerator_model = RepairModel.objects.create(
            repair_brand=cls.refrigerator_brand,
            name="AEG RKE 73211 DM",
            name_ru="AEG RKE 73211 DM",
            name_en="AEG RKE 73211 DM",
            slug="aeg-rke-73211-dm",
        )
        cls.refrigerator_item = CatalogItem.objects.create(
            repair_model=cls.refrigerator_model,
            source_url="https://example.com/aeg-rke-73211-dm",
            product_description="Detailed refrigerator page with specs.",
            product_description_ru="Подробная страница холодильника с характеристиками.",
            product_description_en="Detailed refrigerator page with specs.",
            primary_image="/media/catalog/aeg-rke-73211-dm/image-01.jpg",
            coverage="refrigerator coverage",
            coverage_ru="refrigerator coverage",
            coverage_en="refrigerator coverage",
            short_specs={"Volume": "310 L", "Noise": "37 dB"},
            short_specs_ru={"Объем": "310 л", "Шум": "37 дБ"},
            short_specs_en={"Volume": "310 L", "Noise": "37 dB"},
            seo_title="AEG RKE 73211 DM",
            seo_title_ru="AEG RKE 73211 DM",
            seo_title_en="AEG RKE 73211 DM",
            meta_description="Catalog item meta",
            meta_description_ru="Catalog item meta",
            meta_description_en="Catalog item meta",
        )
        CatalogItemImage.objects.create(
            catalog_item=cls.catalog_item,
            image_url="/media/catalog/lg-f2j6ws0w/image-01.jpg",
            position=0,
        )
        CatalogItemFault.objects.create(
            catalog_item=cls.catalog_item,
            issue="Does not drain",
            likely_causes="Clogged filter",
            first_checks="Clean the filter",
            position=0,
        )

    def test_home_page_loads(self):
        with translation.override("en"):
            response = self.client.get(reverse("portal:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Best Washing Machines 2026")
        self.assertContains(response, "LG F2J6WS0W")
        self.assertContains(response, "Refrigerators")

    def test_root_redirects_to_default_ukrainian_prefix(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/uk/")

    def test_header_text_is_not_mojibake_for_ru_and_uk(self):
        with translation.override("ru"):
            ru_response = self.client.get(reverse("portal:home"))
        self.assertEqual(ru_response.status_code, 200)
        self.assertContains(ru_response, "Техно Портал")
        self.assertContains(ru_response, "Главная")
        self.assertContains(ru_response, "Товары")

        with translation.override("uk"):
            uk_response = self.client.get(reverse("portal:home"))
        self.assertEqual(uk_response.status_code, 200)
        self.assertContains(uk_response, "Техно Портал")
        self.assertContains(uk_response, "Головна")
        self.assertContains(uk_response, "Товари")

    def test_search_placeholder_is_not_mojibake(self):
        with translation.override("ru"):
            ru_response = self.client.get(reverse("portal:home"))
        self.assertEqual(ru_response.status_code, 200)
        self.assertContains(ru_response, 'placeholder="Искать статьи или ошибки ремонта"', html=False)

        with translation.override("uk"):
            uk_response = self.client.get(reverse("portal:home"))
        self.assertEqual(uk_response.status_code, 200)
        self.assertContains(uk_response, 'placeholder="Шукати статті або помилки ремонту"', html=False)

    def test_import_command_normalizes_model_name_without_brand_and_color(self):
        from portal.management.commands.import_items import Command as ImportCommand

        command = ImportCommand()
        command.appliance_type_defaults = {"slug": "refrigerators"}

        self.assertEqual(
            command.normalize_localized_model_name("Whirlpool WPC 82I XP2 нержавіюча сталь", "uk", "Whirlpool"),
            "WPC 82I XP2",
        )
        self.assertEqual(
            command.normalize_localized_model_name("Whirlpool WPC 82I XP2 нержавейка", "ru", "Whirlpool"),
            "WPC 82I XP2",
        )
        self.assertEqual(
            command.normalize_localized_model_name("Whirlpool WPC 82I XP2 stainless steel", "en", "Whirlpool"),
            "WPC 82I XP2",
        )

    def test_article_detail_increments_views(self):
        with translation.override("en"):
            response = self.client.get(self.article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.views, 1)

    def test_product_detail_increments_views(self):
        self.catalog_item.product_description_en = "\n".join(
            [
                "Photo 4",
                "29 746 грн.",
                "example.com ->",
                "Useful product description.",
                "December 12 2025",
            ]
        )
        self.catalog_item.save(update_fields=["product_description_en"])
        with translation.override("en"):
            response = self.client.get(self.catalog_item.get_absolute_url())
            product_url = self.catalog_item.get_absolute_url()
        self.assertEqual(response.status_code, 200)
        self.catalog_item.refresh_from_db()
        self.assertEqual(self.catalog_item.views, 1)
        self.assertIn("/en/items/type/washing-machines/lg-repair/", product_url)
        self.assertContains(response, "Description")
        self.assertContains(response, "Short specs")
        self.assertContains(response, "Useful product description.")
        self.assertNotContains(response, "Photo 4")
        self.assertNotContains(response, "29 746 грн.")
        self.assertNotContains(response, "Search links")

    def test_search_returns_article_error_code_and_product(self):
        with translation.override("en"):
            response = self.client.get(reverse("portal:search"), {"q": "LG"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Best Washing Machines 2026")
        self.assertContains(response, "LG OE error explained")
        self.assertContains(response, "LG F2J6WS0W")

    def test_error_catalog_hierarchy_loads(self):
        with translation.override("en"):
            type_response = self.client.get(reverse("portal:error_list"))
            brand_response = self.client.get(
                reverse("portal:error_type", kwargs={"type_slug": self.appliance_type.slug})
            )
            model_response = self.client.get(
                reverse(
                    "portal:error_brand",
                    kwargs={"type_slug": self.appliance_type.slug, "brand_slug": self.repair_brand.slug},
                )
            )
            detail_response = self.client.get(self.error.get_absolute_url())
        self.assertEqual(type_response.status_code, 200)
        self.assertEqual(brand_response.status_code, 200)
        self.assertEqual(model_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(type_response, "Washing Machines")
        self.assertContains(brand_response, "LG")
        self.assertContains(model_response, "LG F2J6WS0W")

    def test_product_catalog_pages_load(self):
        with translation.override("en"):
            list_response = self.client.get(reverse("portal:product_list"))
            detail_response = self.client.get(self.catalog_item.get_absolute_url())
            refrigerator_response = self.client.get(
                reverse("portal:product_type", kwargs={"type_slug": self.refrigerator_type.slug})
            )
            brand_response = self.client.get(
                reverse(
                    "portal:product_brand",
                    kwargs={"type_slug": self.refrigerator_type.slug, "brand_slug": self.refrigerator_brand.slug},
                )
            )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(refrigerator_response.status_code, 200)
        self.assertEqual(brand_response.status_code, 200)
        self.assertContains(list_response, "LG F2J6WS0W")
        self.assertContains(list_response, "Refrigerators")
        self.assertContains(detail_response, "Does not drain")
        self.assertContains(refrigerator_response, "AEG RKE 73211 DM")
        self.assertNotContains(refrigerator_response, "LG F2J6WS0W")
        self.assertContains(brand_response, "AEG RKE 73211 DM")

    def test_error_brand_page_shows_model_image(self):
        with translation.override("en"):
            response = self.client.get(
                reverse(
                    "portal:error_brand",
                    kwargs={"type_slug": self.appliance_type.slug, "brand_slug": self.repair_brand.slug},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.catalog_item.primary_image)

    def test_product_catalog_pagination_shows_page_links(self):
        for index in range(1, 20):
            repair_model = RepairModel.objects.create(
                repair_brand=self.repair_brand,
                name=f"LG Extra {index}",
                name_ru=f"LG Extra {index}",
                name_en=f"LG Extra {index}",
                slug=f"lg-extra-{index}",
            )
            CatalogItem.objects.create(
                repair_model=repair_model,
                source_url=f"https://example.com/lg-extra-{index}",
                product_description="Extra catalog item.",
                primary_image=f"/media/catalog/lg-extra-{index}/image-01.jpg",
                coverage="extra coverage",
                short_specs={"Load": "6 kg"},
                seo_title=f"LG Extra {index}",
                seo_title_ru=f"LG Extra {index}",
                seo_title_en=f"LG Extra {index}",
                meta_description="Catalog item meta",
                meta_description_ru="Catalog item meta",
                meta_description_en="Catalog item meta",
            )

        with translation.override("en"):
            response = self.client.get(reverse("portal:product_list"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "?page=1")
        self.assertContains(response, 'aria-current="page">2</span>', html=False)
        self.assertContains(response, "LG Extra 9")

    def test_washing_machine_type_page_applies_filters(self):
        six_kg_model = RepairModel.objects.create(
            repair_brand=self.repair_brand,
            name="LG Filter 6",
            name_ru="LG Filter 6",
            name_en="LG Filter 6",
            slug="lg-filter-6",
        )
        CatalogItem.objects.create(
            repair_model=six_kg_model,
            source_url="https://example.com/lg-filter-6",
            product_description="Filterable washer 6 kg.",
            primary_image="/media/catalog/lg-filter-6/image-01.jpg",
            coverage="filter coverage",
            short_specs={
                "Тип завантаження": "фронтальне завантаження",
                "Завантаження": "6 кг",
                "Максимальна швидкість віджимання": "1200 об/хв",
                "Габарити (ВхШхГ)": "85x60x42 см",
            },
            seo_title="LG Filter 6",
            seo_title_ru="LG Filter 6",
            seo_title_en="LG Filter 6",
            meta_description="Catalog item meta",
            meta_description_ru="Catalog item meta",
            meta_description_en="Catalog item meta",
        )
        eight_kg_model = RepairModel.objects.create(
            repair_brand=self.repair_brand,
            name="LG Filter 8",
            name_ru="LG Filter 8",
            name_en="LG Filter 8",
            slug="lg-filter-8",
        )
        CatalogItem.objects.create(
            repair_model=eight_kg_model,
            source_url="https://example.com/lg-filter-8",
            product_description="Filterable washer 8 kg.",
            primary_image="/media/catalog/lg-filter-8/image-01.jpg",
            coverage="filter coverage",
            short_specs={
                "Тип завантаження": "фронтальне завантаження",
                "Завантаження": "8 кг",
                "Максимальна швидкість віджимання": "1400 об/хв",
                "Габарити (ВхШхГ)": "85x60x55 см",
            },
            seo_title="LG Filter 8",
            seo_title_ru="LG Filter 8",
            seo_title_en="LG Filter 8",
            meta_description="Catalog item meta",
            meta_description_ru="Catalog item meta",
            meta_description_en="Catalog item meta",
        )

        with translation.override("uk"):
            response = self.client.get(
                reverse("portal:product_type", kwargs={"type_slug": self.appliance_type.slug}),
                {"load": "6"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LG Filter 6")
        self.assertNotContains(response, "LG Filter 8")

    def test_washing_machine_filters_are_localized(self):
        with translation.override("en"):
            english_response = self.client.get(
                reverse("portal:product_type", kwargs={"type_slug": self.appliance_type.slug})
            )
        self.assertEqual(english_response.status_code, 200)
        self.assertContains(english_response, "Brands")
        self.assertContains(english_response, "Product type")
        self.assertContains(english_response, "Capacity")

        with translation.override("ru"):
            russian_response = self.client.get(
                reverse("portal:product_type", kwargs={"type_slug": self.appliance_type.slug})
            )
        self.assertEqual(russian_response.status_code, 200)
        self.assertContains(russian_response, "Бренды")
        self.assertContains(russian_response, "Тип")
        self.assertContains(russian_response, "Загрузка")

    def test_refrigerator_filters_are_localized(self):
        with translation.override("en"):
            english_response = self.client.get(
                reverse("portal:product_type", kwargs={"type_slug": self.refrigerator_type.slug})
            )
        self.assertEqual(english_response.status_code, 200)
        self.assertContains(english_response, "Brands")
        self.assertContains(english_response, "Product type")
        self.assertContains(english_response, "Number of chambers")
        self.assertContains(english_response, "Freezer")
        self.assertContains(english_response, "Features")

        with translation.override("ru"):
            russian_response = self.client.get(
                reverse("portal:product_type", kwargs={"type_slug": self.refrigerator_type.slug})
            )
        self.assertEqual(russian_response.status_code, 200)
        self.assertContains(russian_response, "Бренды")
        self.assertContains(russian_response, "Тип")
        self.assertContains(russian_response, "Количество камер")
        self.assertContains(russian_response, "Морозилка")
        self.assertContains(russian_response, "Функции и возможности")

    def test_refrigerator_type_page_applies_filters(self):
        side_model = RepairModel.objects.create(
            repair_brand=self.refrigerator_brand,
            name="AEG Side",
            name_ru="AEG Side",
            name_en="AEG Side",
            slug="aeg-side",
        )
        CatalogItem.objects.create(
            repair_model=side_model,
            source_url="https://example.com/aeg-side",
            product_description="Side by side refrigerator.",
            primary_image="/media/catalog/aeg-side/image-01.jpg",
            coverage="fridge coverage",
            short_specs={
                "Тип": "Side-by-side",
                "Кількість камер": "2",
                "Морозильна камера": "збоку",
                "No Frost": "морозильна / холодильна камери",
                "Габарити (ВхШхГ)": "179x91x70 см",
            },
            seo_title="AEG Side",
            seo_title_ru="AEG Side",
            seo_title_en="AEG Side",
            meta_description="Catalog item meta",
            meta_description_ru="Catalog item meta",
            meta_description_en="Catalog item meta",
        )
        classic_model = RepairModel.objects.create(
            repair_brand=self.refrigerator_brand,
            name="AEG Classic",
            name_ru="AEG Classic",
            name_en="AEG Classic",
            slug="aeg-classic",
        )
        CatalogItem.objects.create(
            repair_model=classic_model,
            source_url="https://example.com/aeg-classic",
            product_description="Classic refrigerator.",
            primary_image="/media/catalog/aeg-classic/image-01.jpg",
            coverage="fridge coverage",
            short_specs={
                "Кількість камер": "2",
                "Морозильна камера": "знизу",
                "Габарити (ВхШхГ)": "186x60x65 см",
            },
            seo_title="AEG Classic",
            seo_title_ru="AEG Classic",
            seo_title_en="AEG Classic",
            meta_description="Catalog item meta",
            meta_description_ru="Catalog item meta",
            meta_description_en="Catalog item meta",
        )

        with translation.override("uk"):
            response = self.client.get(
                reverse("portal:product_type", kwargs={"type_slug": self.refrigerator_type.slug}),
                {"fr_type": "side_by_side"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AEG Side")
        self.assertNotContains(response, "AEG Classic")

    def test_product_spec_items_exclude_scraped_noise(self):
        self.catalog_item.short_specs = {
            "Фото 4": "29 746 грн.",
            "Tendo.com.ua →": "29 746 грн.",
            "Колір Характеристики Тип завантаження фронтальне завантаження": "листопад 2020",
            "Тип загрузки": "фронтальная загрузка",
            "Загрузка": "7 кг",
        }
        self.catalog_item.save(update_fields=["short_specs"])

        spec_items = self.catalog_item.spec_items

        self.assertEqual(
            spec_items,
            [("Тип загрузки", "фронтальная загрузка"), ("Загрузка", "7 кг")],
        )

    def test_product_spec_items_exclude_english_scraped_noise(self):
        self.catalog_item.short_specs_en = {
            "Photos 4": "28 271 ₴ Buy! Refrigerator Liebherr CTP 251-21 inSale.com.ua Less than year Delivery: to Dnipro from Kyiv Warranty: 12 month Report add to list my lists add to comparison",
            "Total capacity": "271 L",
            "LED lighting": "yes",
            "Auto-defrost": "yes",
            "Added to E-Catalog": "December 2023",
        }
        self.catalog_item.save(update_fields=["short_specs_en"])

        spec_items = self.catalog_item.clean_spec_items(self.catalog_item.short_specs_en)

        self.assertEqual(
            spec_items,
            [("Total capacity", "271 L"), ("LED lighting", "yes"), ("Auto-defrost", "yes")],
        )

    def test_import_command_localizes_exact_yes_no_spec_values(self):
        from portal.management.commands.import_items import Command as ImportCommand

        command = ImportCommand()

        self.assertEqual(command.localize_spec_value("yes", "uk"), "так")
        self.assertEqual(command.localize_spec_value("yes", "ru"), "да")
        self.assertEqual(command.localize_spec_value("yes", "en"), "yes")
        self.assertEqual(command.localize_spec_value("no", "uk"), "ні")
        self.assertEqual(command.localize_spec_value("no", "ru"), "нет")
        self.assertEqual(command.localize_spec_value("no", "en"), "no")

    def test_generate_product_descriptions_replaces_generic_en_description(self):
        self.catalog_item.product_description_en = (
            "Washing Machine LG F2J6WS0W white at a price from 10000 to 12000 ₴ "
            ">>> E-Katalog - catalog prices comparison & specs ✔ User & media reviews, manuals."
        )
        self.catalog_item.short_specs_en = {
            "Load type": "front loaded",
            "Load": "6 kg",
            "Max. spin speed": "1200 rpm",
            "Number of programmes": "12",
            "Display": "LED",
        }
        self.catalog_item.save(update_fields=["product_description_en", "short_specs_en"])

        call_command("generate_product_descriptions", only_generic=True)

        self.catalog_item.refresh_from_db()
        self.assertNotIn("E-Katalog", self.catalog_item.product_description_en)
        self.assertIn("LG F2J6WS0W", self.catalog_item.product_description_en)
        self.assertIn("6 kg", self.catalog_item.product_description_en)

    def test_generate_product_descriptions_replaces_generic_ru_description(self):
        self.catalog_item.product_description_ru = (
            "Стиральная машина Samsung AddWash WW8NK52E0VW белый по цене от 23331 до 23426 грн. "
            ">>> E-Katalog - каталог сравнение цен и характеристик ✔ Отзывы, обзоры, инструкции."
        )
        self.catalog_item.short_specs = {
            "Тип загрузки": "фронтальная загрузка",
            "Загрузка": "8 кг",
            "Макс. скорость отжима": "1200 об/мин",
            "Количество программ": "14",
            "Дисплей": "LED",
        }
        self.catalog_item.save(update_fields=["product_description_ru", "short_specs"])

        call_command("generate_product_descriptions", only_generic=True)

        self.catalog_item.refresh_from_db()
        self.assertNotIn("E-Katalog", self.catalog_item.product_description_ru)
        self.assertIn("LG F2J6WS0W", self.catalog_item.product_description_ru)
        self.assertIn("8 кг", self.catalog_item.product_description_ru)

    def test_scrub_catalog_metadata_removes_ekatalog_references_and_source_fields(self):
        self.catalog_item.meta_description = (
            "Холодильник Sharp SJ-FBA05DMXLE-EU за ціною від 24706 грн. >>> E-Katalog - каталог порівняння цін."
        )
        self.catalog_item.notes = ["Дата додавання: 2026-03-09"]
        self.catalog_item.notes_ru = ["Дата добавления: 2026-03-09"]
        self.catalog_item.notes_en = ["Added: 2026-03-09"]
        self.catalog_item.model_search_urls = {"uk": "https://ek.ua/ua/SHARP-SJ-FBA05DMXLE-EU.htm"}
        self.catalog_item.source_links = [{"title": "Sharp", "url": "https://ek.ua/ua/SHARP-SJ-FBA05DMXLE-EU.htm"}]
        self.catalog_item.source_links_ru = [{"title": "Sharp", "url": "https://ek.ua/SHARP-SJ-FBA05DMXLE-EU.htm"}]
        self.catalog_item.source_links_en = [{"title": "Sharp", "url": "https://ek.ua/en/SHARP-SJ-FBA05DMXLE-EU.htm"}]
        self.catalog_item.source_url = "https://ek.ua/ua/SHARP-SJ-FBA05DMXLE-EU.htm"
        self.catalog_item.manual_candidates = ["manual.pdf"]
        self.catalog_item.error_info_candidates = ["error"]
        self.catalog_item.save(
            update_fields=[
                "meta_description",
                "notes",
                "notes_ru",
                "notes_en",
                "model_search_urls",
                "source_links",
                "source_links_ru",
                "source_links_en",
                "source_url",
                "manual_candidates",
                "error_info_candidates",
            ]
        )

        call_command("scrub_catalog_metadata")

        self.catalog_item.refresh_from_db()
        self.assertNotIn("E-Katalog", self.catalog_item.meta_description)
        self.assertEqual(self.catalog_item.notes, [])
        self.assertEqual(self.catalog_item.notes_ru, [])
        self.assertEqual(self.catalog_item.notes_en, [])
        self.assertEqual(self.catalog_item.model_search_urls, {})
        self.assertEqual(self.catalog_item.source_links, [])
        self.assertEqual(self.catalog_item.source_links_ru, [])
        self.assertEqual(self.catalog_item.source_links_en, [])
        self.assertEqual(self.catalog_item.source_url, "")
        self.assertEqual(self.catalog_item.manual_candidates, [])
        self.assertEqual(self.catalog_item.error_info_candidates, [])

    def test_sitemap_contains_article_url(self):
        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/uk/articles/best-washing-machines-2026")
        self.assertContains(response, "/uk/items/type/washing-machines/lg-repair/lg-f2j6ws0w/")
