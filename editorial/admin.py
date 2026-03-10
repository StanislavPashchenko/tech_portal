from django.contrib import admin

from editorial.models import AdminArticle


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


@admin.register(AdminArticle)
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
            "Основное",
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
            "Заголовки и анонсы",
            {
                "fields": (
                    ("title", "title_ru", "title_en"),
                    ("excerpt", "excerpt_ru", "excerpt_en"),
                )
            },
        ),
        (
            "Содержимое статьи",
            {
                "fields": (
                    "content",
                    "content_ru",
                    "content_en",
                )
            },
        ),
        ("Публикация", {"fields": ("featured", "is_published", "views")}),
        TranslatedFieldsAdminMixin.seo_fieldset,
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )
