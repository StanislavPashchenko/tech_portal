from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import translation


LANGUAGE_CODES = ("uk", "ru", "en")

CATEGORY_ROUTE_NAMES = {
    "news": "portal:news_list",
    "reviews": "portal:reviews_list",
    "comparisons": "portal:comparisons_list",
    "guides": "portal:guides_list",
    "errors": "portal:error_list",
}


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
    seo_title = models.CharField(max_length=160, default="")
    seo_title_ru = models.CharField(max_length=160, default="")
    seo_title_en = models.CharField(max_length=160, default="")
    meta_description = models.CharField(max_length=255, default="")
    meta_description_ru = models.CharField(max_length=255, default="")
    meta_description_en = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_seo_title(self, language=None):
        return self.get_localized_value("seo_title", language) or str(self)

    def get_meta_description(self, language=None):
        return self.get_localized_value("meta_description", language)


class Category(SeoStampedModel):
    name = models.CharField(max_length=120, default="")
    name_ru = models.CharField(max_length=120, default="")
    name_en = models.CharField(max_length=120, default="")
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(default="")
    description_ru = models.TextField(default="")
    description_en = models.TextField(default="")
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_label(self, language=None):
        return self.get_localized_value("name", language)

    def get_description(self, language=None):
        return self.get_localized_value("description", language)

    def get_absolute_url(self):
        route_name = CATEGORY_ROUTE_NAMES.get(self.slug, "portal:category_index")
        language = self.get_current_language()
        with translation.override(language):
            return reverse(route_name)


class Brand(SeoStampedModel):
    name = models.CharField(max_length=120, default="")
    name_ru = models.CharField(max_length=120, default="")
    name_en = models.CharField(max_length=120, default="")
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(default="")
    description_ru = models.TextField(default="")
    description_en = models.TextField(default="")
    website = models.URLField(blank=True)
    logo = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        language = self.get_current_language()
        with translation.override(language):
            return reverse("portal:brand_detail", kwargs={"slug": self.slug})

    @property
    def display_name(self):
        return self.get_localized_value("name")

    @property
    def display_description(self):
        return self.get_localized_value("description")


class Device(SeoStampedModel):
    name = models.CharField(max_length=160, default="")
    name_ru = models.CharField(max_length=160, default="")
    name_en = models.CharField(max_length=160, default="")
    slug = models.SlugField(max_length=160, unique=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    device_type = models.CharField(max_length=120, default="")
    device_type_ru = models.CharField(max_length=120, default="")
    device_type_en = models.CharField(max_length=120, default="")
    description = models.TextField(default="")
    description_ru = models.TextField(default="")
    description_en = models.TextField(default="")

    class Meta:
        ordering = ["name"]

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
    title = models.CharField(max_length=220, default="")
    title_ru = models.CharField(max_length=220, default="")
    title_en = models.CharField(max_length=220, default="")
    slug = models.SlugField(max_length=220, unique=True)
    content = models.TextField(default="")
    content_ru = models.TextField(default="")
    content_en = models.TextField(default="")
    excerpt = models.TextField(default="")
    excerpt_ru = models.TextField(default="")
    excerpt_en = models.TextField(default="")
    image = models.URLField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name="articles",
        blank=True,
        null=True,
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        related_name="articles",
        blank=True,
        null=True,
    )
    views = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-featured", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        language = self.get_current_language()
        with translation.override(language):
            return reverse(
                "portal:article_detail",
                kwargs={"category_slug": self.category.slug, "slug": self.slug},
            )

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
            | Q(brand__name__icontains=query)
            | Q(brand__name_ru__icontains=query)
            | Q(brand__name_en__icontains=query)
            | Q(device__name__icontains=query)
            | Q(device__name_ru__icontains=query)
            | Q(device__name_en__icontains=query)
        )


class ErrorCode(SeoStampedModel):
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="error_codes",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        related_name="error_codes",
        blank=True,
        null=True,
    )
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=220, default="")
    title_ru = models.CharField(max_length=220, default="")
    title_en = models.CharField(max_length=220, default="")
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(default="")
    description_ru = models.TextField(default="")
    description_en = models.TextField(default="")
    causes = models.TextField(default="")
    causes_ru = models.TextField(default="")
    causes_en = models.TextField(default="")
    solutions = models.TextField(default="")
    solutions_ru = models.TextField(default="")
    solutions_en = models.TextField(default="")
    views = models.PositiveIntegerField(default=0)

    objects = ErrorCodeQuerySet.as_manager()

    class Meta:
        ordering = ["brand__name", "code"]

    def __str__(self):
        return f"{self.brand.name} {self.code}"

    def get_absolute_url(self):
        language = self.get_current_language()
        with translation.override(language):
            return reverse("portal:error_detail", kwargs={"slug": self.slug})

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
