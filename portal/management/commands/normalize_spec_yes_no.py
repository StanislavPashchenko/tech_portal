from django.core.management.base import BaseCommand

from portal.management.commands.import_items import Command as ImportItemsCommand
from portal.models import CatalogItem


FIELD_LANGUAGE_MAP = {
    "short_specs": "uk",
    "short_specs_ru": "ru",
    "short_specs_en": "en",
}


class Command(BaseCommand):
    help = "Normalize exact yes/no values in short_specs to localized variants."

    def handle(self, *args, **options):
        helper = ImportItemsCommand()
        updated = 0

        for item in CatalogItem.objects.all():
            changed_fields = []
            for field, language in FIELD_LANGUAGE_MAP.items():
                specs = getattr(item, field) or {}
                normalized = {}
                changed = False
                for key, value in specs.items():
                    if isinstance(value, str):
                        localized = helper.localize_spec_value(value, language)
                        normalized[key] = localized
                        if localized != value:
                            changed = True
                    else:
                        normalized[key] = value
                if changed:
                    setattr(item, field, normalized)
                    changed_fields.append(field)
            if changed_fields:
                item.save(update_fields=changed_fields)
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Normalized yes/no values for {updated} items"))
