from django.contrib import admin

from portal.models import Article, Brand, Category, Device, ErrorCode


class TranslatedFieldsAdminMixin:
    seo_fieldset = (
        "SEO",
        {
            "fields": (
                ("seo_title", "seo_title_ru", "seo_title_en"),
                (
                    "meta_description",
                    "meta_description_ru",
                    "meta_description_en",
                ),
            )
        },
    )

    def translated_triplet(self, base_name):
        return (base_name, f"{base_name}_ru", f"{base_name}_en")


@admin.register(Category)
class CategoryAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "position", "updated_at")
    list_editable = ("position",)
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = ("name", "name_ru", "name_en", "description", "description_ru", "description_en")
    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "slug",
                    "position",
                )
            },
        ),
        (
            "Ukrainian / Russian / English",
            {
                "fields": (
                    ("name", "name_ru", "name_en"),
                    ("description", "description_ru", "description_en"),
                )
            },
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
    )


@admin.register(Brand)
class BrandAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("name", "website", "updated_at")
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = ("name", "name_ru", "name_en", "description", "description_ru", "description_en")
    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "slug",
                    "website",
                    "logo",
                )
            },
        ),
        (
            "Ukrainian / Russian / English",
            {
                "fields": (
                    ("name", "name_ru", "name_en"),
                    ("description", "description_ru", "description_en"),
                )
            },
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
    )


@admin.register(Device)
class DeviceAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("name", "brand", "category", "device_type", "updated_at")
    list_filter = ("brand", "category")
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = (
        "name",
        "name_ru",
        "name_en",
        "device_type",
        "device_type_ru",
        "device_type_en",
        "description",
        "description_ru",
        "description_en",
    )
    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "slug",
                    "brand",
                    "category",
                )
            },
        ),
        (
            "Ukrainian / Russian / English",
            {
                "fields": (
                    ("name", "name_ru", "name_en"),
                    ("device_type", "device_type_ru", "device_type_en"),
                    ("description", "description_ru", "description_en"),
                )
            },
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
    )


@admin.register(Article)
class ArticleAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("title", "category", "brand", "featured", "views", "updated_at")
    list_filter = ("category", "brand", "featured", "is_published")
    list_select_related = ("category", "brand", "device")
    prepopulated_fields = {"slug": ("title_en",)}
    readonly_fields = ("views", "created_at", "updated_at")
    search_fields = (
        "title",
        "title_ru",
        "title_en",
        "excerpt",
        "excerpt_ru",
        "excerpt_en",
        "content",
        "content_ru",
        "content_en",
    )
    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "slug",
                    "image",
                    "category",
                    "brand",
                    "device",
                )
            },
        ),
        (
            "Titles and Excerpts",
            {
                "fields": (
                    ("title", "title_ru", "title_en"),
                    ("excerpt", "excerpt_ru", "excerpt_en"),
                )
            },
        ),
        (
            "Article Content",
            {
                "fields": (
                    "content",
                    "content_ru",
                    "content_en",
                )
            },
        ),
        ("Publishing", {"fields": ("featured", "is_published", "views")}),
        TranslatedFieldsAdminMixin.seo_fieldset,
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ErrorCode)
class ErrorCodeAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("code", "title", "brand", "device", "views")
    list_filter = ("brand",)
    list_select_related = ("brand", "device")
    prepopulated_fields = {"slug": ("code",)}
    readonly_fields = ("views", "created_at", "updated_at")
    search_fields = (
        "code",
        "title",
        "title_ru",
        "title_en",
        "description",
        "description_ru",
        "description_en",
        "causes",
        "causes_ru",
        "causes_en",
        "solutions",
        "solutions_ru",
        "solutions_en",
    )
    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "brand",
                    "device",
                    "code",
                    "slug",
                    "views",
                )
            },
        ),
        (
            "Ukrainian / Russian / English",
            {
                "fields": (
                    ("title", "title_ru", "title_en"),
                    ("description", "description_ru", "description_en"),
                    ("causes", "causes_ru", "causes_en"),
                    ("solutions", "solutions_ru", "solutions_en"),
                )
            },
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
