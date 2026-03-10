from django.core.management.base import BaseCommand

from portal.management.commands.import_items import Command as ImportItemsCommand
from portal.models import RepairModel


class Command(BaseCommand):
    help = "Remove brand and color suffixes from localized model names."

    def handle(self, *args, **options):
        helper = ImportItemsCommand()
        updated = 0

        for model in RepairModel.objects.select_related("repair_brand").all():
            type_slug = model.repair_brand.appliance_type.slug
            helper.appliance_type_defaults = {"slug": type_slug}
            brand = model.repair_brand.name
            name = helper.normalize_localized_model_name(model.name, "uk", brand)
            name_ru = helper.normalize_localized_model_name(model.name_ru, "ru", model.repair_brand.name_ru or brand)
            name_en = helper.normalize_localized_model_name(model.name_en, "en", model.repair_brand.name_en or brand)

            changed_fields = []
            updates = {
                "name": name,
                "name_ru": name_ru,
                "name_en": name_en,
                "seo_title": name,
                "seo_title_ru": name_ru,
                "seo_title_en": name_en,
            }
            for field, value in updates.items():
                if getattr(model, field) != value:
                    setattr(model, field, value)
                    changed_fields.append(field)

            if changed_fields:
                model.save(update_fields=changed_fields + ["updated_at"])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Normalized {updated} models"))
