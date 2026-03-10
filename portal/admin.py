from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group

from portal.models import (
    CatalogItem,
    CatalogItemFault,
    CatalogItemImage,
    ErrorCode,
    RepairApplianceType,
    RepairBrand,
    RepairModel,
)

admin.site.site_header = "Администрирование Tech Portal"
admin.site.site_title = "Админка Tech Portal"
admin.site.index_title = "Управление контентом"

admin.site.unregister(Group)


class TranslatedFieldsAdminMixin:
    seo_fieldset = (
        "SEO",
        {
            "fields": (
                ("seo_title", "seo_title_ru", "seo_title_en"),
                ("meta_description", "meta_description_ru", "meta_description_en"),
            )
        },
    )


@admin.register(RepairApplianceType)
class RepairApplianceTypeAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "updated_at")
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = ("name", "name_ru", "name_en", "description", "description_ru", "description_en")
    fieldsets = (
        ("Основное", {"fields": ("slug",)}),
        (
            "Название и описание",
            {"fields": (("name", "name_ru", "name_en"), ("description", "description_ru", "description_en"))},
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
    )


@admin.register(RepairBrand)
class RepairBrandAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("name", "appliance_type", "slug", "updated_at")
    list_filter = ("appliance_type",)
    list_select_related = ("appliance_type",)
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = ("name", "name_ru", "name_en", "description", "description_ru", "description_en")
    fieldsets = (
        ("Основное", {"fields": ("appliance_type", "slug")}),
        (
            "Название и описание",
            {"fields": (("name", "name_ru", "name_en"), ("description", "description_ru", "description_en"))},
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
    )


@admin.register(RepairModel)
class RepairModelAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("name", "repair_brand", "slug", "updated_at")
    list_filter = ("repair_brand", "repair_brand__appliance_type")
    list_select_related = ("repair_brand", "repair_brand__appliance_type")
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = ("name", "name_ru", "name_en", "description", "description_ru", "description_en")
    fieldsets = (
        ("Основное", {"fields": ("repair_brand", "slug")}),
        (
            "Название и описание",
            {"fields": (("name", "name_ru", "name_en"), ("description", "description_ru", "description_en"))},
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
    )


class ErrorCodeAdminForm(forms.ModelForm):
    repair_brand = forms.ModelChoiceField(
        label="Бренд",
        queryset=RepairBrand.objects.select_related("appliance_type").order_by("appliance_type__name", "name"),
        required=False,
    )

    class Meta:
        model = ErrorCode
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        brand = None
        instance = getattr(self, "instance", None)
        if instance and instance.pk and instance.repair_model_id:
            brand = instance.repair_model.repair_brand

        if self.data.get("repair_brand"):
            try:
                brand = RepairBrand.objects.get(pk=self.data["repair_brand"])
            except (RepairBrand.DoesNotExist, ValueError, TypeError):
                brand = None

        self.fields["repair_brand"].initial = brand
        self.fields["repair_model"].queryset = RepairModel.objects.none()
        if brand:
            self.fields["repair_model"].queryset = RepairModel.objects.filter(repair_brand=brand).select_related(
                "repair_brand",
                "repair_brand__appliance_type",
            )

    def clean(self):
        cleaned_data = super().clean()
        repair_brand = cleaned_data.get("repair_brand")
        repair_model = cleaned_data.get("repair_model")

        if repair_brand and repair_model and repair_model.repair_brand_id != repair_brand.id:
            self.add_error("repair_model", "Выберите модель из выбранного бренда.")

        if repair_brand and not repair_model:
            self.add_error("repair_model", "Выберите модель.")

        return cleaned_data


@admin.register(ErrorCode)
class ErrorCodeAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    form = ErrorCodeAdminForm
    list_display = ("code", "title", "display_appliance_type", "display_brand_name", "display_model_name", "views")
    list_filter = ("repair_model__repair_brand__appliance_type", "repair_model__repair_brand", "repair_model")
    list_select_related = ("repair_model", "repair_model__repair_brand", "repair_model__repair_brand__appliance_type")
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
        "repair_model__name",
        "repair_model__name_ru",
        "repair_model__name_en",
        "repair_model__repair_brand__name",
        "repair_model__repair_brand__name_ru",
        "repair_model__repair_brand__name_en",
    )
    fieldsets = (
        ("Основное", {"fields": ("repair_brand", "repair_model", "code", "slug", "views")}),
        (
            "Заголовки и описания",
            {"fields": (("title", "title_ru", "title_en"), ("description", "description_ru", "description_en"))},
        ),
        (
            "Причины и решения",
            {"fields": (("causes", "causes_ru", "causes_en"), ("solutions", "solutions_ru", "solutions_en"))},
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )


class CatalogItemImageInline(admin.TabularInline):
    model = CatalogItemImage
    extra = 0


class CatalogItemFaultInline(admin.TabularInline):
    model = CatalogItemFault
    extra = 0


@admin.register(CatalogItem)
class CatalogItemAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("display_name", "display_brand_name", "display_appliance_type", "views", "updated_at")
    list_filter = ("repair_model__repair_brand__appliance_type", "repair_model__repair_brand")
    list_select_related = ("repair_model", "repair_model__repair_brand", "repair_model__repair_brand__appliance_type")
    search_fields = (
        "repair_model__name",
        "repair_model__name_ru",
        "repair_model__name_en",
        "repair_model__repair_brand__name",
        "repair_model__repair_brand__name_ru",
        "repair_model__repair_brand__name_en",
        "product_description",
        "product_description_ru",
        "product_description_en",
        "coverage",
        "coverage_ru",
        "coverage_en",
    )
    readonly_fields = ("views", "created_at", "updated_at")
    inlines = (CatalogItemImageInline, CatalogItemFaultInline)
    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "repair_model",
                    "source_url",
                    ("coverage", "coverage_ru", "coverage_en"),
                    "primary_image",
                    "category_image",
                    "views",
                )
            },
        ),
        ("Описание", {"fields": ("product_description", "short_specs")}),
        (
            "Данные ремонта",
            {
                "fields": ("repair_tips",)
            },
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )


admin.site.unregister(CatalogItem)


@admin.register(CatalogItem)
class CatalogItemLocalizedAdmin(TranslatedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ("display_name", "display_brand_name", "display_appliance_type", "views", "updated_at")
    list_filter = ("repair_model__repair_brand__appliance_type", "repair_model__repair_brand")
    list_select_related = ("repair_model", "repair_model__repair_brand", "repair_model__repair_brand__appliance_type")
    search_fields = (
        "repair_model__name",
        "repair_model__name_ru",
        "repair_model__name_en",
        "repair_model__repair_brand__name",
        "repair_model__repair_brand__name_ru",
        "repair_model__repair_brand__name_en",
        "product_description",
        "product_description_ru",
        "product_description_en",
        "coverage",
        "coverage_ru",
        "coverage_en",
    )
    readonly_fields = ("views", "created_at", "updated_at")
    inlines = (CatalogItemImageInline, CatalogItemFaultInline)
    fieldsets = (
        (
            "????????",
            {
                "fields": (
                    "repair_model",
                    "source_url",
                    ("coverage", "coverage_ru", "coverage_en"),
                    "primary_image",
                    "category_image",
                    "views",
                )
            },
        ),
        (
            "????????",
            {"fields": (("product_description", "product_description_ru", "product_description_en"),)},
        ),
        (
            "??????????????",
            {"fields": (("short_specs", "short_specs_ru", "short_specs_en"),)},
        ),
        (
            "?????? ???????",
            {
                "fields": (("repair_tips", "repair_tips_ru", "repair_tips_en"),)
            },
        ),
        TranslatedFieldsAdminMixin.seo_fieldset,
        ("????", {"fields": ("created_at", "updated_at")}),
    )
