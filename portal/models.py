import re

from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import translation


LANGUAGE_CODES = ("uk", "ru", "en")

NOISY_DESCRIPTION_PATTERNS = (
    r"^\s*Фото\s+\d+\s*$",
    r"^\s*Photo\s+\d+\s*$",
    r"^\s*\d[\d\s]*[.,]?\d*\s*(грн\.?|₴)\s*$",
    r"^\s*[\w.-]+\.(com|ua|net|org)(?:\s*[→-]+)?\s*$",
    r"^\s*Отзыв полезен\?.*$",
    r"^\s*(Да|Нет)\s+\d+\s+(Да|Нет)\s+\d+\s*$",
    r"^\s*\d{1,2}\s+[А-Яа-яІіЇїЄєA-Za-z]+\s+\d{4}\s*$",
    r"^\s*[A-Za-z]+\s+\d{1,2}\s+\d{4}\s*$",
    r"^\s*Вердикт:\s*.*$",
)

GENERIC_DESCRIPTION_PATTERNS = {
    "uk": (
        "e-katalog",
        "за ціною від",
        "каталог порівняння цін",
    ),
    "ru": (
        "e-katalog",
        "по цене от",
        "каталог сравнения цен",
    ),
    "en": (
        "e-katalog",
        "at a price from",
        "catalog prices comparison",
    ),
}

GENERIC_DESCRIPTION_REGEXES = (
    r"(?:at a price from|по цене от|за ціною від)",
    r"(?:catalog prices comparison|каталог сравнение цен|каталог порівняння цін)",
    r">>>\s*e-katalog",
    r"(?:user\s*&\s*media reviews|отзывы,\s*обзоры,\s*инструкции|відгуки,\s*огляди,\s*інструкції)",
)

EKATALOG_REFERENCE_REGEXES = (
    r"\bek\.ua\b",
    r"\be-katalog\b",
    r">>>\s*e-katalog",
)

NOISY_SPEC_PATTERNS = (
    r"^\s*Фото\s+\d+\s*$",
    r"^\s*Photo\s+\d+\s*$",
    r"^\s*Photos\s+\d+\s*$",
    r"^\s*\d[\d\s]*[.,]?\d*\s*(грн\.?|₴)\s*$",
    r"^\s*[\w.-]+\.(com|ua|net|org)(?:\s*[→-]+)?\s*$",
    r"^\s*Купити!.*$",
    r"^\s*Buy!.*$",
    r"^\s*Поскаржитись.*$",
    r"^\s*Report.*$",
    r"^\s*в\s+список.*$",
    r"^\s*додати\s+до\s+порівняння.*$",
    r"^.*\bLess than year\b.*$",
    r"^.*\badd to list\b.*$",
    r"^.*\badd to comparison\b.*$",
)


class MultilingualModelMixin(models.Model):
    class Meta:
        abstract = True

    def get_current_language(self, language=None):
        return (language or translation.get_language() or "uk")[:2]

    def get_localized_value(self, field_name, language=None):
        language = self.get_current_language(language)
        candidates = [language, "uk", "ru", "en"]
        seen = set()
        for code in candidates:
            if code in seen:
                continue
            seen.add(code)
            attr_name = field_name if code == "uk" else f"{field_name}_{code}"
            value = getattr(self, attr_name, "")
            if value:
                return value
        return ""


class SeoStampedModel(MultilingualModelMixin, models.Model):
    seo_title = models.CharField("SEO-заголовок (укр.)", max_length=160, default="")
    seo_title_ru = models.CharField("SEO-заголовок (рус.)", max_length=160, default="")
    seo_title_en = models.CharField("SEO-заголовок (англ.)", max_length=160, default="")
    meta_description = models.CharField("Meta description (укр.)", max_length=255, default="")
    meta_description_ru = models.CharField("Meta description (рус.)", max_length=255, default="")
    meta_description_en = models.CharField("Meta description (англ.)", max_length=255, default="")
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        abstract = True

    def get_seo_title(self, language=None):
        return self.get_localized_value("seo_title", language) or str(self)

    def get_meta_description(self, language=None):
        return self.get_localized_value("meta_description", language)


class NamedSlugSeoModel(SeoStampedModel):
    name = models.CharField("Название (укр.)", max_length=160, default="")
    name_ru = models.CharField("Название (рус.)", max_length=160, default="")
    name_en = models.CharField("Название (англ.)", max_length=160, default="")
    slug = models.SlugField("Слаг", max_length=180, unique=True)
    description = models.TextField("Описание (укр.)", default="", blank=True)
    description_ru = models.TextField("Описание (рус.)", default="", blank=True)
    description_en = models.TextField("Описание (англ.)", default="", blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.get_localized_value("name")

    @property
    def display_description(self):
        return self.get_localized_value("description")


class Category(SeoStampedModel):
    name = models.CharField("Название (укр.)", max_length=120, default="")
    name_ru = models.CharField("Название (рус.)", max_length=120, default="")
    name_en = models.CharField("Название (англ.)", max_length=120, default="")
    slug = models.SlugField("Слаг", max_length=120, unique=True)
    description = models.TextField("Описание (укр.)", default="")
    description_ru = models.TextField("Описание (рус.)", default="")
    description_en = models.TextField("Описание (англ.)", default="")
    position = models.PositiveIntegerField("Позиция", default=0)

    class Meta:
        ordering = ["position", "name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_label(self, language=None):
        return self.get_localized_value("name", language)

    def get_description(self, language=None):
        return self.get_localized_value("description", language)

    def get_absolute_url(self):
        language = self.get_current_language()
        with translation.override(language):
            return reverse("portal:home")


class Brand(SeoStampedModel):
    name = models.CharField("Название (укр.)", max_length=120, default="")
    name_ru = models.CharField("Название (рус.)", max_length=120, default="")
    name_en = models.CharField("Название (англ.)", max_length=120, default="")
    slug = models.SlugField("Слаг", max_length=120, unique=True)
    description = models.TextField("Описание (укр.)", default="")
    description_ru = models.TextField("Описание (рус.)", default="")
    description_en = models.TextField("Описание (англ.)", default="")
    website = models.URLField("Сайт", blank=True)
    logo = models.URLField("Логотип", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        language = self.get_current_language()
        with translation.override(language):
            return reverse("portal:home")

    @property
    def display_name(self):
        return self.get_localized_value("name")

    @property
    def display_description(self):
        return self.get_localized_value("description")


class Device(SeoStampedModel):
    name = models.CharField("Название (укр.)", max_length=160, default="")
    name_ru = models.CharField("Название (рус.)", max_length=160, default="")
    name_en = models.CharField("Название (англ.)", max_length=160, default="")
    slug = models.SlugField("Слаг", max_length=160, unique=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name="Бренд",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name="Категория",
    )
    device_type = models.CharField("Тип устройства (укр.)", max_length=120, default="")
    device_type_ru = models.CharField("Тип устройства (рус.)", max_length=120, default="")
    device_type_en = models.CharField("Тип устройства (англ.)", max_length=120, default="")
    description = models.TextField("Описание (укр.)", default="")
    description_ru = models.TextField("Описание (рус.)", default="")
    description_en = models.TextField("Описание (англ.)", default="")

    class Meta:
        ordering = ["name"]
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        return self.get_localized_value("name")

    @property
    def display_description(self):
        return self.get_localized_value("description")

    @property
    def display_device_type(self):
        return self.get_localized_value("device_type")


class RepairApplianceType(NamedSlugSeoModel):
    class Meta:
        ordering = ["name"]
        verbose_name = "Тип техники"
        verbose_name_plural = "Типы техники"


class RepairBrand(NamedSlugSeoModel):
    appliance_type = models.ForeignKey(
        RepairApplianceType,
        on_delete=models.CASCADE,
        related_name="repair_brands",
        verbose_name="Тип техники",
    )

    class Meta:
        ordering = ["appliance_type__name", "name"]
        unique_together = ("appliance_type", "slug")
        verbose_name = "Бренд техники"
        verbose_name_plural = "Бренды техники"


class RepairModel(NamedSlugSeoModel):
    repair_brand = models.ForeignKey(
        RepairBrand,
        on_delete=models.CASCADE,
        related_name="repair_models",
        verbose_name="Бренд",
    )

    class Meta:
        ordering = ["repair_brand__name", "name"]
        unique_together = ("repair_brand", "slug")
        verbose_name = "Модель техники"
        verbose_name_plural = "Модели техники"

    @property
    def appliance_type(self):
        return self.repair_brand.appliance_type


class CatalogItemQuerySet(models.QuerySet):
    def search(self, query):
        return self.filter(
            Q(repair_model__name__icontains=query)
            | Q(repair_model__name_ru__icontains=query)
            | Q(repair_model__name_en__icontains=query)
            | Q(repair_model__repair_brand__name__icontains=query)
            | Q(repair_model__repair_brand__name_ru__icontains=query)
            | Q(repair_model__repair_brand__name_en__icontains=query)
            | Q(repair_model__repair_brand__appliance_type__name__icontains=query)
            | Q(repair_model__repair_brand__appliance_type__name_ru__icontains=query)
            | Q(repair_model__repair_brand__appliance_type__name_en__icontains=query)
            | Q(product_description__icontains=query)
            | Q(coverage__icontains=query)
        )


class CatalogItem(SeoStampedModel):
    repair_model = models.OneToOneField(
        RepairModel,
        on_delete=models.CASCADE,
        related_name="catalog_item",
        verbose_name="Модель техніки",
    )
    source_url = models.URLField("URL товару", blank=True)
    product_description = models.TextField("Опис товару", default="", blank=True)
    product_description_ru = models.TextField("Опис товару (рус.)", default="", blank=True)
    product_description_en = models.TextField("Опис товару (англ.)", default="", blank=True)
    category_image = models.URLField("Зображення категорії", blank=True)
    primary_image = models.CharField("Головне зображення", max_length=255, default="", blank=True)
    coverage = models.CharField("Покриття ремонту", max_length=255, default="", blank=True)
    coverage_ru = models.CharField("Покриття ремонту (рус.)", max_length=255, default="", blank=True)
    coverage_en = models.CharField("Покриття ремонту (англ.)", max_length=255, default="", blank=True)
    short_specs = models.JSONField("Короткі характеристики", default=dict, blank=True)
    short_specs_ru = models.JSONField("Короткі характеристики (рус.)", default=dict, blank=True)
    short_specs_en = models.JSONField("Короткі характеристики (англ.)", default=dict, blank=True)
    repair_tips = models.JSONField("Поради з ремонту", default=list, blank=True)
    repair_tips_ru = models.JSONField("Поради з ремонту (рус.)", default=list, blank=True)
    repair_tips_en = models.JSONField("Поради з ремонту (англ.)", default=list, blank=True)
    notes = models.JSONField("Нотатки", default=list, blank=True)
    notes_ru = models.JSONField("Нотатки (рус.)", default=list, blank=True)
    notes_en = models.JSONField("Нотатки (англ.)", default=list, blank=True)
    model_search_urls = models.JSONField("Пошукові посилання", default=dict, blank=True)
    source_links = models.JSONField("Джерела", default=list, blank=True)
    source_links_ru = models.JSONField("Джерела (рус.)", default=list, blank=True)
    source_links_en = models.JSONField("Джерела (англ.)", default=list, blank=True)
    manual_candidates = models.JSONField("Кандидати мануалів", default=list, blank=True)
    error_info_candidates = models.JSONField("Кандидати помилок", default=list, blank=True)
    views = models.PositiveIntegerField("Перегляди", default=0)

    objects = CatalogItemQuerySet.as_manager()

    class Meta:
        ordering = [
            "repair_model__repair_brand__appliance_type__name",
            "repair_model__repair_brand__name",
            "repair_model__name",
        ]
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return self.display_name

    def get_absolute_url(self):
        language = self.get_current_language()
        with translation.override(language):
            return reverse(
                "portal:product_detail",
                kwargs={
                    "type_slug": self.repair_model.repair_brand.appliance_type.slug,
                    "brand_slug": self.repair_model.repair_brand.slug,
                    "slug": self.repair_model.slug,
                },
            )

    @property
    def display_name(self):
        return self.repair_model.display_name

    @property
    def display_brand_name(self):
        return self.repair_model.repair_brand.display_name

    @property
    def display_appliance_type(self):
        return self.repair_model.repair_brand.appliance_type.display_name

    @property
    def spec_items(self):
        return self.clean_spec_items(self.get_localized_value("short_specs") or {})

    @property
    def display_product_description(self):
        language = self.get_current_language()
        value = self.clean_product_description(self.get_localized_value("product_description", language))
        if self.is_generic_product_description(value, language):
            return self.generate_product_description(language)
        return value

    @property
    def display_coverage(self):
        return self.get_localized_value("coverage")

    @property
    def display_repair_tips(self):
        return self.get_localized_value("repair_tips") or []

    @property
    def display_notes(self):
        return self.get_localized_value("notes") or []

    @property
    def display_source_links(self):
        return self.get_localized_value("source_links") or self.source_links or []

    @property
    def display_source_url(self):
        first_source = next(iter(self.display_source_links), None)
        if isinstance(first_source, dict):
            return first_source.get("url") or self.source_url
        return self.source_url

    @classmethod
    def clean_product_description(cls, value):
        if not value:
            return ""

        lines = []
        seen = set()
        for raw_line in re.split(r"[\r\n]+", value):
            line = re.sub(r"\s+", " ", raw_line).strip(" \t-")
            if not line:
                continue
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in NOISY_DESCRIPTION_PATTERNS):
                continue
            if line.lower() in seen:
                continue
            seen.add(line.lower())
            lines.append(line)

        cleaned = "\n".join(lines).strip()
        if len(cleaned) < 40:
            return ""
        return cleaned

    @staticmethod
    def is_generic_product_description(value, language):
        if not value:
            return True
        normalized = value.lower()
        if all(token in normalized for token in GENERIC_DESCRIPTION_PATTERNS.get(language, ())):
            return True
        if "e-katalog" not in normalized:
            return False
        match_count = sum(
            1 for pattern in GENERIC_DESCRIPTION_REGEXES if re.search(pattern, normalized, re.IGNORECASE)
        )
        return match_count >= 2

    @staticmethod
    def contains_ekatalog_reference(value):
        normalized = (value or "").lower()
        if not normalized:
            return False
        return any(re.search(pattern, normalized, re.IGNORECASE) for pattern in EKATALOG_REFERENCE_REGEXES)

    @classmethod
    def clean_spec_items(cls, specs):
        cleaned_items = []
        seen = set()

        for key, value in (specs or {}).items():
            clean_key = re.sub(r"\s+", " ", str(key or "")).strip(" \t-")
            clean_value = re.sub(r"\s+", " ", str(value or "")).strip(" \t-")
            combined = f"{clean_key} {clean_value}".strip()

            if not clean_key or not clean_value:
                continue
            if any(re.match(pattern, clean_key, re.IGNORECASE) for pattern in NOISY_SPEC_PATTERNS):
                continue
            if any(re.match(pattern, clean_value, re.IGNORECASE) for pattern in NOISY_SPEC_PATTERNS):
                continue
            if "e-katalog" in clean_key.lower() or "e-katalog" in clean_value.lower():
                continue
            if "e-catalog" in clean_key.lower() or "e-catalog" in clean_value.lower():
                continue
            if "Характеристики" in clean_key or "Характеристики" in clean_value:
                continue
            if "Characteristics" in clean_key or "Characteristics" in clean_value:
                continue
            if len(clean_key) > 80:
                continue
            if len(clean_value) > 180:
                continue
            if combined.lower() in seen:
                continue

            seen.add(combined.lower())
            cleaned_items.append((clean_key, clean_value))

        return cleaned_items

    def get_clean_specs(self, language=None):
        return dict(self.clean_spec_items(self.get_localized_value("short_specs", language) or {}))

    def generate_product_description(self, language=None):
        language = self.get_current_language(language)
        specs = self.get_clean_specs(language)
        if not specs:
            return ""

        brand = self.display_brand_name
        model = self.display_name
        type_slug = self.repair_model.repair_brand.appliance_type.slug

        if type_slug == "washing-machines":
            return self.generate_washing_machine_description(language, brand, model, specs)
        if type_slug == "refrigerators":
            return self.generate_refrigerator_description(language, brand, model, specs)
        return self.generate_generic_description(language, brand, model, specs)

    @staticmethod
    def _join_list(parts, language):
        parts = [part for part in parts if part]
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        if language == "ru":
            return ", ".join(parts[:-1]) + " и " + parts[-1]
        if language == "uk":
            return ", ".join(parts[:-1]) + " та " + parts[-1]
        return ", ".join(parts[:-1]) + " and " + parts[-1]

    def generate_washing_machine_description(self, language, brand, model, specs):
        load_type = specs.get("Тип завантаження") or specs.get("Тип загрузки") or specs.get("Load type")
        capacity = specs.get("Завантаження") or specs.get("Загрузка") or specs.get("Load")
        spin = specs.get("Максимальна швидкість віджимання") or specs.get("Макс. скорость отжима") or specs.get("Max. spin speed")
        dry_load = specs.get("Завантаження для сушіння") or specs.get("Загрузка для сушки") or specs.get("Drying load")
        dimensions = specs.get("Габарити (ВхШхГ)") or specs.get("Габариты (ВхШхГ)") or specs.get("Dimensions (HxWxD)")
        programs = specs.get("Кількість програм") or specs.get("Количество программ") or specs.get("Number of programmes")
        control = specs.get("Управління") or specs.get("Управление") or specs.get("Control")
        display = specs.get("Дисплей") or specs.get("Display")
        smart = specs.get("Управління зі смартфона") or specs.get("Управление со смартфона") or specs.get("Smart control")
        features = []
        for key in (
            "Інверторний двигун",
            "Инверторный двигатель",
            "Inverter motor",
            "Прання паром",
            "Стирка паром",
            "Steam wash",
        ):
            value = specs.get(key)
            if value:
                features.append(f"{key} {value}" if value.lower() not in {"yes", "так", "да"} else key)

        if language == "uk":
            sentence1 = f"Пральна машина {brand} {model}"
            if load_type:
                sentence1 += f" з {load_type.lower()}"
            if capacity:
                sentence1 += f" і завантаженням до {capacity}"
            sentence1 += "."
            details = []
            if spin:
                details.append(f"віджимання до {spin}")
            if dry_load:
                details.append(f"сушіння до {dry_load}")
            if dimensions:
                details.append(f"габарити {dimensions}")
            sentence2 = ""
            if details:
                sentence2 = "Модель пропонує " + self._join_list(details, language) + "."
            extras = []
            if programs:
                extras.append(f"{programs} програм")
            if control:
                extras.append(f"керування {control.lower()}")
            if display:
                extras.append(f"дисплей {display}")
            if smart:
                extras.append(f"підтримку {smart}")
            if features:
                extras.extend(features[:2])
            sentence3 = ""
            if extras:
                sentence3 = "Серед особливостей варто відзначити " + self._join_list(extras, language) + "."
            return " ".join(part for part in (sentence1, sentence2, sentence3) if part)

        if language == "ru":
            sentence1 = f"Стиральная машина {brand} {model}"
            if load_type:
                sentence1 += f" с {load_type.lower()}"
            if capacity:
                sentence1 += f" и загрузкой до {capacity}"
            sentence1 += "."
            details = []
            if spin:
                details.append(f"отжим до {spin}")
            if dry_load:
                details.append(f"сушка до {dry_load}")
            if dimensions:
                details.append(f"габариты {dimensions}")
            sentence2 = ""
            if details:
                sentence2 = "Модель предлагает " + self._join_list(details, language) + "."
            extras = []
            if programs:
                extras.append(f"{programs} программ")
            if control:
                extras.append(f"управление {control.lower()}")
            if display:
                extras.append(f"дисплей {display}")
            if smart:
                extras.append(f"поддержку {smart}")
            if features:
                extras.extend(features[:2])
            sentence3 = ""
            if extras:
                sentence3 = "Среди особенностей можно отметить " + self._join_list(extras, language) + "."
            return " ".join(part for part in (sentence1, sentence2, sentence3) if part)

        sentence1 = f"The {brand} {model} washing machine"
        if load_type:
            sentence1 += f" features {load_type.lower()}"
        if capacity:
            sentence1 += f" with a load capacity of {capacity}"
        sentence1 += "."
        details = []
        if spin:
            details.append(f"spin speed up to {spin}")
        if dry_load:
            details.append(f"drying capacity up to {dry_load}")
        if dimensions:
            details.append(f"dimensions of {dimensions}")
        sentence2 = ""
        if details:
            sentence2 = "It offers " + self._join_list(details, language) + "."
        extras = []
        if programs:
            extras.append(f"{programs} programmes")
        if control:
            extras.append(f"{control.lower()} controls")
        if display:
            extras.append(f"a {display} display")
        if smart:
            extras.append(f"{smart} support")
        if features:
            extras.extend(features[:2])
        sentence3 = ""
        if extras:
            sentence3 = "Notable features include " + self._join_list(extras, language) + "."
        return " ".join(part for part in (sentence1, sentence2, sentence3) if part)

    def generate_refrigerator_description(self, language, brand, model, specs):
        total_volume = specs.get("Загальний об'єм") or specs.get("Общий объем") or specs.get("Total capacity")
        freezer = specs.get("Об'єм морозильної камери") or specs.get("Объем морозильной камеры") or specs.get("Freezer capacity")
        fresh = specs.get("Об'єм холодильної камери") or specs.get("Объем холодильной камеры") or specs.get("Fridge capacity")
        no_frost = specs.get("No Frost") or specs.get("No frost")
        dimensions = specs.get("Габарити (ВхШхГ)") or specs.get("Габариты (ВхШхГ)") or specs.get("Dimensions (HxWxD)")
        noise = specs.get("Рівень шуму") or specs.get("Уровень шума") or specs.get("Noise level")
        compressor = specs.get("Кількість компресорів") or specs.get("Количество компрессоров") or specs.get("Compressors")

        if language == "uk":
            parts = [f"Холодильник {brand} {model}"]
            if total_volume:
                parts.append(f"із загальним об'ємом {total_volume}")
            text = " ".join(parts) + "."
            details = []
            if fresh:
                details.append(f"холодильне відділення {fresh}")
            if freezer:
                details.append(f"морозильна камера {freezer}")
            if noise:
                details.append(f"рівень шуму {noise}")
            if dimensions:
                details.append(f"габарити {dimensions}")
            if no_frost:
                details.append("система No Frost")
            if compressor:
                details.append(f"{compressor} компресор")
            if details:
                text += " Модель пропонує " + self._join_list(details, language) + "."
            return text

        if language == "ru":
            parts = [f"Холодильник {brand} {model}"]
            if total_volume:
                parts.append(f"с общим объемом {total_volume}")
            text = " ".join(parts) + "."
            details = []
            if fresh:
                details.append(f"холодильное отделение {fresh}")
            if freezer:
                details.append(f"морозильная камера {freezer}")
            if noise:
                details.append(f"уровень шума {noise}")
            if dimensions:
                details.append(f"габариты {dimensions}")
            if no_frost:
                details.append("система No Frost")
            if compressor:
                details.append(f"{compressor} компрессор")
            if details:
                text += " Модель предлагает " + self._join_list(details, language) + "."
            return text

        parts = [f"The {brand} {model} refrigerator"]
        if total_volume:
            parts.append(f"offers a total capacity of {total_volume}")
        text = " ".join(parts) + "."
        details = []
        if fresh:
            details.append(f"fridge compartment {fresh}")
        if freezer:
            details.append(f"freezer capacity {freezer}")
        if noise:
            details.append(f"noise level of {noise}")
        if dimensions:
            details.append(f"dimensions of {dimensions}")
        if no_frost:
            details.append("No Frost cooling")
        if compressor:
            details.append(f"{compressor} compressor")
        if details:
            text += " It includes " + self._join_list(details, language) + "."
        return text

    def generate_generic_description(self, language, brand, model, specs):
        first_specs = list(specs.items())[:4]
        if language == "uk":
            text = f"Модель {brand} {model} належить до категорії {self.display_appliance_type.lower()}."
            if first_specs:
                text += " Серед основних характеристик: " + self._join_list(
                    [f"{key.lower()} {value}" for key, value in first_specs], language
                ) + "."
            return text
        if language == "ru":
            text = f"Модель {brand} {model} относится к категории {self.display_appliance_type.lower()}."
            if first_specs:
                text += " Среди основных характеристик: " + self._join_list(
                    [f"{key.lower()} {value}" for key, value in first_specs], language
                ) + "."
            return text
        text = f"The {brand} {model} model belongs to the {self.display_appliance_type.lower()} category."
        if first_specs:
            text += " Key specifications include " + self._join_list(
                [f"{key.lower()} {value}" for key, value in first_specs], language
            ) + "."
        return text


class CatalogItemImage(models.Model):
    catalog_item = models.ForeignKey(
        CatalogItem,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
    )
    image_url = models.CharField("Зображення", max_length=255)
    position = models.PositiveIntegerField("Позиція", default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Зображення товару"
        verbose_name_plural = "Зображення товарів"

    def __str__(self):
        return f"{self.catalog_item.display_name} #{self.position + 1}"


class CatalogItemFault(models.Model):
    catalog_item = models.ForeignKey(
        CatalogItem,
        on_delete=models.CASCADE,
        related_name="faults",
        verbose_name="Товар",
    )
    issue = models.CharField("Несправність", max_length=255)
    likely_causes = models.TextField("Ймовірні причини", default="", blank=True)
    first_checks = models.TextField("Перші перевірки", default="", blank=True)
    position = models.PositiveIntegerField("Позиція", default=0)

    class Meta:
        ordering = ["position", "issue"]
        verbose_name = "Типова несправність"
        verbose_name_plural = "Типові несправності"

    def __str__(self):
        return self.issue


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def localized(self, language):
        return self

    def search(self, query):
        return self.filter(
            Q(title__icontains=query)
            | Q(title_ru__icontains=query)
            | Q(title_en__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(excerpt_ru__icontains=query)
            | Q(excerpt_en__icontains=query)
            | Q(content__icontains=query)
            | Q(content_ru__icontains=query)
            | Q(content_en__icontains=query)
            | Q(brand__name__icontains=query)
            | Q(brand__name_ru__icontains=query)
            | Q(brand__name_en__icontains=query)
            | Q(device__name__icontains=query)
            | Q(device__name_ru__icontains=query)
            | Q(device__name_en__icontains=query)
        )


class Article(SeoStampedModel):
    title = models.CharField("Заголовок (укр.)", max_length=220, default="")
    title_ru = models.CharField("Заголовок (рус.)", max_length=220, default="")
    title_en = models.CharField("Заголовок (англ.)", max_length=220, default="")
    slug = models.SlugField("Слаг", max_length=220, unique=True)
    content = models.TextField("Контент (укр.)", default="")
    content_ru = models.TextField("Контент (рус.)", default="")
    content_en = models.TextField("Контент (англ.)", default="")
    excerpt = models.TextField("Краткое описание (укр.)", default="")
    excerpt_ru = models.TextField("Краткое описание (рус.)", default="")
    excerpt_en = models.TextField("Краткое описание (англ.)", default="")
    image = models.URLField("Изображение", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="Категория",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name="articles",
        blank=True,
        null=True,
        verbose_name="Бренд",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        related_name="articles",
        blank=True,
        null=True,
        verbose_name="Устройство",
    )
    views = models.PositiveIntegerField("Просмотры", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)
    featured = models.BooleanField("Рекомендуемое", default=False)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-featured", "-created_at"]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        language = self.get_current_language()
        with translation.override(language):
            return reverse("portal:article_detail", kwargs={"slug": self.slug})

    @property
    def display_title(self):
        return self.get_localized_value("title")

    @property
    def display_excerpt(self):
        return self.get_localized_value("excerpt")

    @property
    def display_content(self):
        return self.get_localized_value("content")


class ErrorCodeQuerySet(models.QuerySet):
    def localized(self, language):
        return self

    def search(self, query):
        return self.filter(
            Q(code__icontains=query)
            | Q(title__icontains=query)
            | Q(title_ru__icontains=query)
            | Q(title_en__icontains=query)
            | Q(description__icontains=query)
            | Q(description_ru__icontains=query)
            | Q(description_en__icontains=query)
            | Q(causes__icontains=query)
            | Q(causes_ru__icontains=query)
            | Q(causes_en__icontains=query)
            | Q(solutions__icontains=query)
            | Q(solutions_ru__icontains=query)
            | Q(solutions_en__icontains=query)
            | Q(repair_model__name__icontains=query)
            | Q(repair_model__name_ru__icontains=query)
            | Q(repair_model__name_en__icontains=query)
            | Q(repair_model__repair_brand__name__icontains=query)
            | Q(repair_model__repair_brand__name_ru__icontains=query)
            | Q(repair_model__repair_brand__name_en__icontains=query)
            | Q(repair_model__repair_brand__appliance_type__name__icontains=query)
            | Q(repair_model__repair_brand__appliance_type__name_ru__icontains=query)
            | Q(repair_model__repair_brand__appliance_type__name_en__icontains=query)
        )


class ErrorCode(SeoStampedModel):
    repair_model = models.ForeignKey(
        RepairModel,
        on_delete=models.CASCADE,
        related_name="error_codes",
        verbose_name="Модель техники",
        blank=True,
        null=True,
    )
    code = models.CharField("Код/поломка", max_length=80)
    title = models.CharField("Заголовок (укр.)", max_length=220, default="")
    title_ru = models.CharField("Заголовок (рус.)", max_length=220, default="")
    title_en = models.CharField("Заголовок (англ.)", max_length=220, default="")
    slug = models.SlugField("Слаг", max_length=220, unique=True)
    description = models.TextField("Описание (укр.)", default="")
    description_ru = models.TextField("Описание (рус.)", default="")
    description_en = models.TextField("Описание (англ.)", default="")
    causes = models.TextField("Причины (укр.)", default="")
    causes_ru = models.TextField("Причины (рус.)", default="")
    causes_en = models.TextField("Причины (англ.)", default="")
    solutions = models.TextField("Решения (укр.)", default="")
    solutions_ru = models.TextField("Решения (рус.)", default="")
    solutions_en = models.TextField("Решения (англ.)", default="")
    views = models.PositiveIntegerField("Просмотры", default=0)

    objects = ErrorCodeQuerySet.as_manager()

    class Meta:
        ordering = [
            "repair_model__repair_brand__appliance_type__name",
            "repair_model__repair_brand__name",
            "repair_model__name",
            "code",
        ]
        verbose_name = "Ошибка ремонта"
        verbose_name_plural = "Ошибки ремонта"

    def __str__(self):
        return f"{self.display_brand_name} {self.code}"

    def get_absolute_url(self):
        language = self.get_current_language()
        with translation.override(language):
            return reverse(
                "portal:error_detail",
                kwargs={
                    "type_slug": self.repair_model.repair_brand.appliance_type.slug,
                    "brand_slug": self.repair_model.repair_brand.slug,
                    "model_slug": self.repair_model.slug,
                    "slug": self.slug,
                },
            )

    @property
    def display_title(self):
        return self.get_localized_value("title")

    @property
    def display_description(self):
        return self.get_localized_value("description")

    @property
    def display_causes(self):
        return self.get_localized_value("causes")

    @property
    def display_solutions(self):
        return self.get_localized_value("solutions")

    @property
    def display_brand_name(self):
        if not self.repair_model_id:
            return ""
        return self.repair_model.repair_brand.display_name

    @property
    def display_appliance_type(self):
        if not self.repair_model_id:
            return ""
        return self.repair_model.repair_brand.appliance_type.display_name

    @property
    def display_model_name(self):
        if not self.repair_model_id:
            return ""
        return self.repair_model.display_name
