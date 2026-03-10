import json
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from portal.models import (
    CatalogItem,
    CatalogItemFault,
    CatalogItemImage,
    ErrorCode,
    RepairApplianceType,
    RepairBrand,
    RepairModel,
)


class Command(BaseCommand):
    help = "Import parsed product and repair data from the items directory."

    APPLIANCE_TYPE_PRESETS = {
        "washing-machines": {
            "slug": "washing-machines",
            "name": "Пральні машини",
            "name_ru": "Стиральные машины",
            "name_en": "Washing machines",
            "description": "Каталог пральних машин з характеристиками, фото та базовими даними для ремонту.",
            "description_ru": "Каталог стиральных машин с характеристиками, фото и базовыми данными для ремонта.",
            "description_en": "Catalog of washing machines with specifications, photos, and basic repair data.",
            "seo_title": "Пральні машини",
            "seo_title_ru": "Стиральные машины",
            "seo_title_en": "Washing machines",
            "meta_description": "Каталог пральних машин з фото, описом і характеристиками.",
            "meta_description_ru": "Каталог стиральных машин с фото, описанием и характеристиками.",
            "meta_description_en": "Catalog of washing machines with photos, descriptions, and specifications.",
        },
        "refrigerators": {
            "slug": "refrigerators",
            "name": "Холодильники",
            "name_ru": "Холодильники",
            "name_en": "Refrigerators",
            "description": "Каталог холодильників з характеристиками, фото та базовими даними для ремонту.",
            "description_ru": "Каталог холодильников с характеристиками, фото и базовыми данными для ремонта.",
            "description_en": "Catalog of refrigerators with specifications, photos, and basic repair data.",
            "seo_title": "Холодильники",
            "seo_title_ru": "Холодильники",
            "seo_title_en": "Refrigerators",
            "meta_description": "Каталог холодильників з фото, описом і характеристиками.",
            "meta_description_ru": "Каталог холодильников с фото, описанием и характеристиками.",
            "meta_description_en": "Catalog of refrigerators with photos, descriptions, and specifications.",
        },
    }
    SPEC_LABEL_FIXES = {
        "ru": {
            "Інтелектуальне прання": "Интеллектуальная стирка",
            "Повітряно-бульбашкове прання": "Воздушно-пузырьковая стирка",
            "Люк дозавантаження білизни": "Люк догрузки белья",
            "Голосовий асистент": "Голосовой помощник",
        },
        "en": {
            "Інтелектуальне прання": "Intelligent wash",
            "Повітряно-бульбашкове прання": "Air bubble wash",
            "Люк дозавантаження білизни": "Laundry add hatch",
            "Голосовий асистент": "Voice assistant",
        },
    }
    SPEC_VALUE_FIXES = {
        "ru": {
            "нічна": "ночная",
            "кут відкриття дверей": "угол открытия дверцы",
            "кут відкриття люка": "угол открытия люка",
            "кут відкриття Lюка": "угол открытия люка",
            "кВт/рік": "кВт/год",
            "кВт год/рік": "кВтч/год",
            "Румунія": "Румыния",
            "Росія": "Россия",
            "нікельоване покриття": "никелированное покрытие",
            "нікеLьоване покриття": "никелированное покрытие",
            "з керамічним покриттям": "с керамическим покрытием",
            "ліворуч/праворуч": "влево/вправо",
            "Lіворуч/праворуч": "влево/вправо",
            "прання+сушіння": "стирка+сушка",
            "цикL": "цикл",
            "рік": "год",
        },
        "en": {
            "нічна": "night wash",
            "кут відкриття дверей": "door opening angle",
            "кут відкриття люка": "hatch opening angle",
            "кут відкриття Lюка": "hatch opening angle",
            "кВт/рік": "kWh/year",
            "кВт год/рік": "kWh/year",
            "Румунія": "Romania",
            "Росія": "Russia",
            "нікельоване покриття": "nickel-plated coating",
            "нікеLьоване покриття": "nickel-plated coating",
            "з керамічним покриттям": "ceramic-coated",
            "ліворуч/праворуч": "left/right",
            "Lіворуч/праворуч": "left/right",
            "прання+сушіння": "wash+dry",
            "цикL": "cycle",
            "рік": "year",
        },
    }
    MODEL_PREFIXES_BY_LANGUAGE = {
        "uk": ("машина ", "пральна машина ", "прально-сушильна машина "),
        "ru": ("машина ", "стиральная машина ", "стирально-сушильная машина "),
        "en": ("washing machine ", "washer ", "washer-dryer "),
    }
    GENERIC_BRAND_VALUES = {
        "",
        "пральна",
        "стиральная",
        "washing",
        "washer",
        "washer-dryer",
        "холодильник",
        "refrigerator",
        "fridge",
    }
    MODEL_COLOR_SUFFIXES = {
        "uk": (
            "нержавіюча сталь",
            "червоний",
            "чорний",
            "сріблястий",
            "сірий",
            "графіт",
            "білий",
            "бежевий",
            "синій",
            "зелений",
            "коричневий",
            "бронзовий",
            "золотистий",
        ),
        "ru": (
            "нержавеющая сталь",
            "нержавейка",
            "красный",
            "черный",
            "серебристый",
            "серый",
            "графит",
            "белый",
            "бежевый",
            "синий",
            "зеленый",
            "коричневый",
            "бронзовый",
            "золотистый",
        ),
        "en": (
            "stainless steel",
            "stainless",
            "silver",
            "graphite",
            "black",
            "white",
            "gray",
            "grey",
            "red",
            "blue",
            "green",
            "beige",
            "brown",
            "bronze",
            "gold",
        ),
    }
    SAFETY_SPEC_LABELS = {
        "uk": {
            "leak_protection": "Захист від протікання",
            "foam_control": "Контроль піноутворення",
            "imbalance_control": "Контроль дисбалансу",
            "child_lock": "Захист від дітей",
        },
        "ru": {
            "leak_protection": "Защита от протечек",
            "foam_control": "Контроль пенообразования",
            "imbalance_control": "Контроль дисбаланса",
            "child_lock": "Защита от детей",
        },
        "en": {
            "leak_protection": "Leak protection",
            "foam_control": "Anti-foam control",
            "imbalance_control": "Unbalance control",
            "child_lock": "Child lock",
        },
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--items-dir",
            default=str(settings.BASE_DIR / "items"),
            help="Directory with parsed item folders.",
        )
        parser.add_argument(
            "--appliance-type",
            choices=sorted(self.APPLIANCE_TYPE_PRESETS.keys()),
            default="washing-machines",
            help="Target appliance type slug.",
        )

    def handle(self, *args, **options):
        items_dir = Path(options["items_dir"])
        if not items_dir.exists():
            self.stdout.write(self.style.ERROR(f"Directory not found: {items_dir}"))
            return

        self.appliance_type_defaults = self.APPLIANCE_TYPE_PRESETS[options["appliance_type"]]

        imported = 0
        for item_dir in sorted(path for path in items_dir.iterdir() if path.is_dir()):
            with transaction.atomic():
                if not self.import_item(item_dir):
                    continue
                imported += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {imported} items from {items_dir}"))

    def import_item(self, item_dir):
        product_data, localized_data = self.load_item_payload(item_dir)
        if not product_data:
            return False

        appliance_type = self.get_or_create_appliance_type()
        repair_brand = self.get_or_create_brand(product_data, appliance_type)
        repair_model = self.get_or_create_model(product_data, localized_data, repair_brand)

        product_description_uk = self.build_product_description(product_data, localized_data.get("uk", {}), "uk")
        product_description_ru = self.build_product_description(product_data, localized_data.get("ru", {}), "ru")
        product_description_en = self.build_product_description(product_data, localized_data.get("en", {}), "en")
        source_links_uk = self.build_source_links(product_data, localized_data, "uk")
        source_links_ru = self.build_source_links(product_data, localized_data, "ru")
        source_links_en = self.build_source_links(product_data, localized_data, "en")
        notes_uk = self.build_notes(product_data, localized_data.get("uk", {}), "uk")
        notes_ru = self.build_notes(product_data, localized_data.get("ru", {}), "ru")
        notes_en = self.build_notes(product_data, localized_data.get("en", {}), "en")

        catalog_item, _ = CatalogItem.objects.update_or_create(
            repair_model=repair_model,
            defaults={
                "source_url": "",
                "product_description": product_description_uk,
                "product_description_ru": product_description_ru,
                "product_description_en": product_description_en,
                "category_image": product_data.get("category_image", "") or product_data.get("list_image", ""),
                "primary_image": "",
                "coverage": appliance_type.name,
                "coverage_ru": appliance_type.name_ru,
                "coverage_en": appliance_type.name_en,
                "short_specs": self.merge_specs(
                    self.normalize_specs(localized_data.get("uk", {}).get("full_specifications"), "uk")
                    or self.normalize_specs(product_data.get("short_specs"), "uk"),
                    localized_data.get("uk", {}).get("safety_features"),
                ),
                "short_specs_ru": self.merge_specs(
                    self.normalize_specs(localized_data.get("ru", {}).get("full_specifications"), "ru"),
                    localized_data.get("ru", {}).get("safety_features"),
                ),
                "short_specs_en": self.merge_specs(
                    self.normalize_specs(localized_data.get("en", {}).get("full_specifications"), "en"),
                    localized_data.get("en", {}).get("safety_features"),
                ),
                "repair_tips": [],
                "repair_tips_ru": [],
                "repair_tips_en": [],
                "notes": notes_uk,
                "notes_ru": notes_ru,
                "notes_en": notes_en,
                "model_search_urls": {},
                "source_links": source_links_uk,
                "source_links_ru": source_links_ru,
                "source_links_en": source_links_en,
                "manual_candidates": [],
                "error_info_candidates": [],
                "seo_title": localized_data.get("uk", {}).get("title") or repair_model.name,
                "seo_title_ru": localized_data.get("ru", {}).get("title") or repair_model.name_ru,
                "seo_title_en": localized_data.get("en", {}).get("title") or repair_model.name_en,
                "meta_description": self.build_meta_description(localized_data.get("uk", {}), product_description_uk, "uk"),
                "meta_description_ru": self.build_meta_description(localized_data.get("ru", {}), product_description_ru, "ru"),
                "meta_description_en": self.build_meta_description(localized_data.get("en", {}), product_description_en, "en"),
            },
        )

        image_urls = self.import_images(catalog_item, item_dir, product_data)
        primary_image = image_urls[0] if image_urls else product_data.get("category_image", "")
        if catalog_item.primary_image != primary_image:
            catalog_item.primary_image = primary_image
            catalog_item.save(update_fields=["primary_image", "updated_at"])

        self.replace_faults(catalog_item, [])
        self.replace_error_codes(repair_model, [])
        return True

    def load_item_payload(self, item_dir):
        product_path = item_dir / "product.json"
        if product_path.exists():
            product_data = json.loads(product_path.read_text(encoding="utf-8-sig"))
            return product_data, self.load_localized_product_data(item_dir, product_data)

        trilang_paths = {language: item_dir / f"{language}.json" for language in ("ua", "ru", "en")}
        if not trilang_paths["ua"].exists() and not trilang_paths["en"].exists():
            return None, {}

        trilang_data = {}
        for language, file_path in trilang_paths.items():
            if file_path.exists():
                trilang_data[language] = json.loads(file_path.read_text(encoding="utf-8-sig"))
        return self.normalize_trilang_payload(trilang_data)

    def load_localized_product_data(self, item_dir, product_data):
        localized_data = {}
        language_files = product_data.get("language_files", {})
        for language in ("uk", "ru", "en"):
            file_name = language_files.get(language) or f"product.{language}.json"
            file_path = item_dir / file_name
            if file_path.exists():
                localized_data[language] = json.loads(file_path.read_text(encoding="utf-8-sig"))
            else:
                localized_data[language] = {}
        return localized_data

    def normalize_trilang_payload(self, trilang_data):
        base_data = trilang_data.get("ua") or trilang_data.get("en") or trilang_data.get("ru") or {}
        product = base_data.get("product", {})
        source = base_data.get("source", {})
        pricing = base_data.get("pricing", {})
        localized_data = {}

        for source_language, target_language in (("ua", "uk"), ("ru", "ru"), ("en", "en")):
            data = trilang_data.get(source_language, {})
            localized_product = data.get("product", {})
            localized_data[target_language] = {
                "brand": localized_product.get("brand") or "",
                "model": self.normalize_localized_model_name(
                    localized_product.get("model") or "",
                    target_language,
                    localized_product.get("brand") or "",
                ),
                "title": localized_product.get("title") or localized_product.get("model") or "",
                "description": data.get("description") or "",
                "meta_description": (data.get("description") or "")[:255],
                "full_specifications": self.flatten_specs(data),
                "safety_features": self.extract_safety_feature_specs(data.get("features"), target_language),
                "product_url": data.get("source", {}).get("actual_url") or data.get("source", {}).get("url") or "",
                "item_added_date": data.get("source", {}).get("retrieved_on") or "",
            }

        product_data = {
            "brand": self.resolve_brand_name(localized_data, product),
            "brand_ru": self.resolve_brand_name(localized_data, product),
            "brand_en": self.resolve_brand_name(localized_data, product),
            "model": product.get("model") or "",
            "model_ru": localized_data.get("ru", {}).get("model") or product.get("model") or "",
            "model_en": localized_data.get("en", {}).get("model") or product.get("model") or "",
            "product_url": source.get("actual_url") or source.get("url") or "",
            "language_urls": {
                language: payload.get("product_url", "")
                for language, payload in localized_data.items()
                if payload.get("product_url")
            },
            "short_specs": localized_data.get("uk", {}).get("full_specifications", {}),
            "item_added_date": source.get("retrieved_on") or "",
            "price_text": self.build_price_text(pricing),
            "official_site_url": self.extract_official_site(base_data),
            "downloaded_images": [Path(path).name for path in base_data.get("local_images", [])],
            "image_links": base_data.get("images", []),
        }
        return product_data, localized_data

    def flatten_specs(self, data):
        raw_specs = data.get("raw_specs") or {}
        flattened = {}
        if not isinstance(raw_specs, dict):
            return flattened
        for group_specs in raw_specs.values():
            if not isinstance(group_specs, dict):
                continue
            for label, value in group_specs.items():
                flattened[str(label)] = value
        return flattened

    def extract_safety_feature_specs(self, features, language):
        if not isinstance(features, dict):
            return {}
        labels = self.SAFETY_SPEC_LABELS.get(language, {})
        specs = {}
        for key, label in labels.items():
            if features.get(key) is True:
                specs[label] = self.localize_spec_value("yes", language)
        return specs

    def merge_specs(self, specs, extra_specs):
        merged = dict(specs or {})
        for key, value in (extra_specs or {}).items():
            merged.setdefault(key, value)
        return merged

    def build_price_text(self, pricing):
        if not isinstance(pricing, dict):
            return ""
        currency = pricing.get("currency") or ""
        min_price = pricing.get("min_price")
        max_price = pricing.get("max_price")
        if min_price and max_price and min_price != max_price:
            return f"{min_price}-{max_price} {currency}".strip()
        if min_price:
            return f"{min_price} {currency}".strip()
        if max_price:
            return f"{max_price} {currency}".strip()
        return ""

    def extract_official_site(self, data):
        raw_specs = data.get("raw_specs") or {}
        for group_specs in raw_specs.values():
            if not isinstance(group_specs, dict):
                continue
            for label, value in group_specs.items():
                label_text = str(label).lower()
                if "official website" in label_text or "офіційний сайт" in label_text or "официальный сайт" in label_text:
                    return str(value).strip()
        return ""

    def get_or_create_appliance_type(self):
        slug = self.appliance_type_defaults["slug"]
        obj, created = RepairApplianceType.objects.get_or_create(
            slug=slug,
            defaults=self.appliance_type_defaults,
        )
        if not created:
            changed_fields = []
            for field, value in self.appliance_type_defaults.items():
                if field == "slug":
                    continue
                if getattr(obj, field) != value:
                    setattr(obj, field, value)
                    changed_fields.append(field)
            if changed_fields:
                obj.save(update_fields=changed_fields + ["updated_at"])
        return obj

    def get_or_create_brand(self, product_data, appliance_type):
        brand_name = (product_data.get("brand") or "Unknown").strip()
        brand_name_ru = (product_data.get("brand_ru") or brand_name or "Unknown").strip()
        brand_name_en = (product_data.get("brand_en") or brand_name or "Unknown").strip()
        base_slug = slugify(brand_name_en or brand_name) or "unknown-brand"
        descriptions = {
            "description": f"Бренд {brand_name} у категорії {appliance_type.name.lower()}.",
            "description_ru": f"Бренд {brand_name_ru} в категории {appliance_type.name_ru.lower()}.",
            "description_en": f"{brand_name_en} brand in the {appliance_type.name_en.lower()} category.",
        }
        obj = (
            RepairBrand.objects.filter(appliance_type=appliance_type, name_en=brand_name_en).first()
            or RepairBrand.objects.filter(appliance_type=appliance_type, name=brand_name).first()
            or RepairBrand.objects.filter(appliance_type=appliance_type, name_ru=brand_name_ru).first()
        )
        created = obj is None
        if created:
            slug = self.ensure_unique_slug(
                RepairBrand,
                base_slug,
                lookup_filters={"appliance_type": appliance_type},
                fallback_prefix=appliance_type.slug,
            )
            obj = RepairBrand(
                appliance_type=appliance_type,
                slug=slug,
            )
        changed_fields = []
        updates = {
            "name": brand_name,
            "name_ru": brand_name_ru,
            "name_en": brand_name_en,
            **descriptions,
            "seo_title": brand_name,
            "seo_title_ru": brand_name_ru,
            "seo_title_en": brand_name_en,
            "meta_description": descriptions["description"][:255],
            "meta_description_ru": descriptions["description_ru"][:255],
            "meta_description_en": descriptions["description_en"][:255],
        }
        for field, value in updates.items():
            if getattr(obj, field) != value:
                setattr(obj, field, value)
                changed_fields.append(field)
        if created:
            obj.save()
        elif changed_fields:
            obj.save(update_fields=changed_fields + ["updated_at"])
        return obj

    def get_or_create_model(self, product_data, localized_data, repair_brand):
        model_name = (
            localized_data.get("uk", {}).get("model")
            or product_data.get("model")
            or "Unknown model"
        ).strip()
        model_name_ru = (
            localized_data.get("ru", {}).get("model")
            or product_data.get("model_ru")
            or model_name
        ).strip()
        model_name_en = (
            localized_data.get("en", {}).get("model")
            or product_data.get("model_en")
            or model_name
        ).strip()
        base_slug = slugify(model_name_en or model_name) or slugify(f"{repair_brand.slug}-model")
        slug = self.ensure_unique_slug(
            RepairModel,
            base_slug,
            lookup_filters={"repair_brand": repair_brand},
            fallback_prefix=repair_brand.slug,
        )
        description_uk = self.build_product_description(product_data, localized_data.get("uk", {}), "uk")
        description_ru = self.build_product_description(product_data, localized_data.get("ru", {}), "ru")
        description_en = self.build_product_description(product_data, localized_data.get("en", {}), "en")
        obj, created = RepairModel.objects.get_or_create(
            repair_brand=repair_brand,
            slug=slug,
            defaults={
                "name": model_name,
                "name_ru": model_name_ru,
                "name_en": model_name_en,
                "description": description_uk,
                "description_ru": description_ru,
                "description_en": description_en,
                "seo_title": model_name,
                "seo_title_ru": model_name_ru,
                "seo_title_en": model_name_en,
                "meta_description": description_uk[:255],
                "meta_description_ru": description_ru[:255],
                "meta_description_en": description_en[:255],
            },
        )
        if not created:
            obj.name = model_name
            obj.name_ru = model_name_ru
            obj.name_en = model_name_en
            obj.description = description_uk
            obj.description_ru = description_ru
            obj.description_en = description_en
            obj.seo_title = model_name
            obj.seo_title_ru = model_name_ru
            obj.seo_title_en = model_name_en
            obj.meta_description = description_uk[:255]
            obj.meta_description_ru = description_ru[:255]
            obj.meta_description_en = description_en[:255]
            obj.save()
        return obj

    def build_product_description(self, product_data, localized_product_data, language):
        localized_description = (localized_product_data.get("description") or "").strip()
        if localized_description:
            cleaned_description = CatalogItem.clean_product_description(localized_description)
            cleaned_description = self.localize_spec_value(cleaned_description, language)
            if cleaned_description and not CatalogItem.is_generic_product_description(cleaned_description, language):
                return cleaned_description

        title = localized_product_data.get("title") or product_data.get("model") or ""
        specs = self.normalize_specs(localized_product_data.get("full_specifications"), language)
        fragments = [title.strip()]
        if specs:
            first_items = list(specs.items())[:3]
            fragments.extend(f"{label} {self.stringify_value(value, language)}" for label, value in first_items)
        brand = (product_data.get("brand") or "").strip()
        if language == "uk":
            suffix = f"Модель {brand} з фото та характеристиками." if brand else "Модель з фото та характеристиками."
        elif language == "ru":
            suffix = f"Модель {brand} с фото и характеристиками." if brand else "Модель с фото и характеристиками."
        else:
            suffix = f"{brand} model with photos and specifications." if brand else "Model with photos and specifications."
        fragments.append(suffix)
        return ". ".join(part for part in fragments if part).strip()

    def build_meta_description(self, localized_product_data, fallback_description, language):
        value = ((localized_product_data.get("meta_description") or "").strip() or fallback_description).strip()
        if CatalogItem.contains_ekatalog_reference(value) or CatalogItem.is_generic_product_description(value, language):
            value = (fallback_description or "").strip()
        return value[:255]

    def build_source_links(self, product_data, localized_data, language):
        return []

    def build_notes(self, product_data, localized_product_data, language):
        return []
        notes = []
        item_added_date = localized_product_data.get("item_added_date") or product_data.get("item_added_date")
        if item_added_date:
            if language == "uk":
                notes.append(f"Дата додавання: {item_added_date}")
            elif language == "ru":
                notes.append(f"Дата добавления: {item_added_date}")
            else:
                notes.append(f"Added: {item_added_date}")
        if product_data.get("price_text"):
            if language == "uk":
                notes.append(f"Ціна: {product_data['price_text']}")
            elif language == "ru":
                notes.append(f"Цена: {product_data['price_text']}")
            else:
                notes.append(f"Price: {product_data['price_text']}")
        if product_data.get("official_site_url"):
            if language == "uk":
                notes.append(f"Офіційний сайт: {product_data['official_site_url']}")
            elif language == "ru":
                notes.append(f"Официальный сайт: {product_data['official_site_url']}")
            else:
                notes.append(f"Official site: {product_data['official_site_url']}")
        return notes

    def normalize_specs(self, specs, language="uk"):
        if not isinstance(specs, dict):
            return {}
        normalized = {}
        for label, value in specs.items():
            normalized[self.localize_spec_label(str(label), language)] = self.stringify_value(value, language)
        return normalized

    def stringify_value(self, value, language="uk"):
        if value is True:
            return {"uk": "Так", "ru": "Да", "en": "Yes"}.get(language, "Yes")
        if value is False:
            return {"uk": "Ні", "ru": "Нет", "en": "No"}.get(language, "No")
        if value is None:
            return ""
        return self.localize_spec_value(str(value).strip(), language)

    def localize_spec_label(self, value, language):
        return self.SPEC_LABEL_FIXES.get(language, {}).get(value, value)

    def localize_spec_value(self, value, language):
        normalized = (value or "").strip()
        lowered = normalized.lower()
        if lowered == "yes":
            return {"uk": "так", "ru": "да", "en": "yes"}.get(language, "yes")
        if lowered == "no":
            return {"uk": "ні", "ru": "нет", "en": "no"}.get(language, "no")

        localized_value = normalized
        for source, target in self.SPEC_VALUE_FIXES.get(language, {}).items():
            localized_value = localized_value.replace(source, target)
        return localized_value

    def resolve_brand_name(self, localized_data, product):
        candidates = [
            localized_data.get("en", {}).get("brand"),
            localized_data.get("ru", {}).get("brand"),
            localized_data.get("uk", {}).get("brand"),
            product.get("brand"),
        ]
        for candidate in candidates:
            normalized = (candidate or "").strip()
            if normalized and normalized.lower() not in self.GENERIC_BRAND_VALUES:
                return normalized

        model_candidates = [
            localized_data.get("en", {}).get("model"),
            localized_data.get("ru", {}).get("model"),
            localized_data.get("uk", {}).get("model"),
            product.get("model"),
        ]
        for candidate in model_candidates:
            inferred = self.infer_brand_from_model(candidate)
            if inferred:
                return inferred
        return "Unknown"

    def infer_brand_from_model(self, value):
        normalized = (value or "").strip()
        if not normalized:
            return ""
        parts = normalized.split()
        if not parts:
            return ""
        first = parts[0].strip("()[]")
        if first.lower() in self.GENERIC_BRAND_VALUES:
            return parts[1].strip("()[]") if len(parts) > 1 else ""
        return first

    def normalize_localized_model_name(self, value, language, brand=""):
        normalized = (value or "").strip()
        normalized = self.strip_brand_prefix(normalized, brand)
        normalized = self.strip_model_color_suffix(normalized, language)
        if self.appliance_type_defaults.get("slug") != "washing-machines":
            return normalized.strip()

        lowered = normalized.lower()
        for prefix in self.MODEL_PREFIXES_BY_LANGUAGE.get(language, ()):
            if lowered.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
                break
        return self.strip_model_color_suffix(normalized, language).strip()

    def strip_brand_prefix(self, value, brand):
        normalized = (value or "").strip()
        brand = (brand or "").strip()
        if not normalized or not brand:
            return normalized
        pattern = rf"^{re.escape(brand)}\s+"
        return re.sub(pattern, "", normalized, count=1, flags=re.IGNORECASE).strip()

    def strip_model_color_suffix(self, value, language):
        normalized = (value or "").strip()
        if not normalized:
            return normalized

        for suffix in sorted(self.MODEL_COLOR_SUFFIXES.get(language, ()), key=len, reverse=True):
            pattern = rf"\s+{re.escape(suffix)}(?=(?:\s*\([^)]*\))?\s*$)"
            updated = re.sub(pattern, "", normalized, flags=re.IGNORECASE).strip()
            if updated != normalized:
                return updated
        return normalized

    def ensure_unique_slug(self, model_class, base_slug, lookup_filters, fallback_prefix):
        existing = model_class.objects.filter(**lookup_filters, slug=base_slug).first()
        if existing:
            return existing.slug
        if not model_class.objects.filter(slug=base_slug).exists():
            return base_slug

        candidate = slugify(f"{fallback_prefix}-{base_slug}") or base_slug
        if not model_class.objects.filter(slug=candidate).exists():
            return candidate

        index = 2
        while True:
            numbered_candidate = f"{candidate}-{index}"
            if not model_class.objects.filter(slug=numbered_candidate).exists():
                return numbered_candidate
            index += 1

    def import_images(self, catalog_item, item_dir, product_data):
        CatalogItemImage.objects.filter(catalog_item=catalog_item).delete()
        image_urls = []
        downloaded_images = product_data.get("downloaded_images", [])
        if isinstance(downloaded_images, str):
            downloaded_images = [downloaded_images]
        elif not isinstance(downloaded_images, list):
            downloaded_images = []
        image_links = product_data.get("image_links", [])

        for index, source in enumerate(downloaded_images):
            source_path = Path(source)
            if not source_path.exists():
                source_path = item_dir / "images" / source_path.name
            copied_url = self.copy_image(source_path, catalog_item.repair_model.slug, index)
            if copied_url:
                image_urls.append(copied_url)

        if not image_urls:
            image_urls.extend(image_links)

        for index, image_url in enumerate(image_urls):
            CatalogItemImage.objects.create(catalog_item=catalog_item, image_url=image_url, position=index)

        return image_urls

    def copy_image(self, source_path, model_slug, index):
        if not source_path.exists() or not source_path.is_file():
            return ""
        target_dir = Path(settings.MEDIA_ROOT) / "catalog" / model_slug
        target_dir.mkdir(parents=True, exist_ok=True)
        extension = source_path.suffix.lower() or ".jpg"
        target_path = target_dir / f"image-{index + 1:02d}{extension}"
        shutil.copy2(source_path, target_path)
        return f"{settings.MEDIA_URL}catalog/{model_slug}/{target_path.name}"

    def replace_faults(self, catalog_item, faults):
        CatalogItemFault.objects.filter(catalog_item=catalog_item).delete()
        for index, fault in enumerate(faults):
            CatalogItemFault.objects.create(
                catalog_item=catalog_item,
                issue=fault.get("issue", ""),
                likely_causes="\n".join(fault.get("likely_causes", [])),
                first_checks="\n".join(fault.get("first_checks", [])),
                position=index,
            )

    def replace_error_codes(self, repair_model, error_codes):
        ErrorCode.objects.filter(repair_model=repair_model).delete()
        for index, error_data in enumerate(error_codes):
            code = (error_data.get("code") or f"issue-{index + 1}").strip()
            meaning = error_data.get("meaning", "").strip()
            title = f"{repair_model.name} {code}: {meaning}".strip(": ")
            slug = slugify(f"{repair_model.slug}-{code}") or f"{repair_model.slug}-{index + 1}"
            ErrorCode.objects.create(
                repair_model=repair_model,
                code=code,
                slug=slug,
                title=title,
                title_ru=title,
                title_en=title,
                description=meaning,
                description_ru=meaning,
                description_en=meaning,
                causes="\n".join(error_data.get("common_causes", [])),
                causes_ru="\n".join(error_data.get("common_causes", [])),
                causes_en="\n".join(error_data.get("common_causes", [])),
                solutions="\n".join(error_data.get("first_checks", [])),
                solutions_ru="\n".join(error_data.get("first_checks", [])),
                solutions_en="\n".join(error_data.get("first_checks", [])),
                seo_title=title[:160],
                seo_title_ru=title[:160],
                seo_title_en=title[:160],
                meta_description=meaning[:255],
                meta_description_ru=meaning[:255],
                meta_description_en=meaning[:255],
            )
