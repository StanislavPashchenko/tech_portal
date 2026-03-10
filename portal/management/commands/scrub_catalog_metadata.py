from django.core.management.base import BaseCommand

from portal.models import CatalogItem, RepairModel


DESCRIPTION_FIELDS = (
    ("uk", "product_description", "meta_description"),
    ("ru", "product_description_ru", "meta_description_ru"),
    ("en", "product_description_en", "meta_description_en"),
)

MODEL_DESCRIPTION_FIELDS = (
    ("uk", "description", "meta_description"),
    ("ru", "description_ru", "meta_description_ru"),
    ("en", "description_en", "meta_description_en"),
)


class Command(BaseCommand):
    help = "Remove E-Katalog references and clear imported source metadata from catalog items."

    def handle(self, *args, **options):
        updated_items = 0
        updated_models = 0

        for item in CatalogItem.objects.select_related(
            "repair_model",
            "repair_model__repair_brand",
            "repair_model__repair_brand__appliance_type",
        ):
            changed_fields = []

            for language, description_field, meta_field in DESCRIPTION_FIELDS:
                description = getattr(item, description_field) or ""
                cleaned_description = item.clean_product_description(description)
                if item.is_generic_product_description(cleaned_description, language):
                    cleaned_description = item.generate_product_description(language)
                    if cleaned_description and cleaned_description != description:
                        setattr(item, description_field, cleaned_description)
                        changed_fields.append(description_field)

                meta_value = getattr(item, meta_field) or ""
                if not meta_value or item.contains_ekatalog_reference(meta_value):
                    replacement = (cleaned_description or "").strip()[:255]
                    if getattr(item, meta_field) != replacement:
                        setattr(item, meta_field, replacement)
                        changed_fields.append(meta_field)

            zero_fields = {
                "source_url": "",
                "notes": [],
                "notes_ru": [],
                "notes_en": [],
                "model_search_urls": {},
                "source_links": [],
                "source_links_ru": [],
                "source_links_en": [],
                "manual_candidates": [],
                "error_info_candidates": [],
            }
            for field, replacement in zero_fields.items():
                if getattr(item, field) != replacement:
                    setattr(item, field, replacement)
                    changed_fields.append(field)

            if changed_fields:
                item.save(update_fields=list(dict.fromkeys(changed_fields)))
                updated_items += 1

        for model in RepairModel.objects.all():
            changed_fields = []
            for language, description_field, meta_field in MODEL_DESCRIPTION_FIELDS:
                description = getattr(model, description_field) or ""
                if not description:
                    continue
                if CatalogItem.contains_ekatalog_reference(description):
                    replacement = ""
                    if getattr(model, meta_field) != replacement:
                        setattr(model, meta_field, replacement)
                        changed_fields.append(meta_field)
                elif CatalogItem.contains_ekatalog_reference(getattr(model, meta_field) or ""):
                    replacement = description[:255]
                    if getattr(model, meta_field) != replacement:
                        setattr(model, meta_field, replacement)
                        changed_fields.append(meta_field)
            if changed_fields:
                model.save(update_fields=list(dict.fromkeys(changed_fields)))
                updated_models += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Scrubbed {updated_items} catalog items and {updated_models} repair models."
            )
        )
