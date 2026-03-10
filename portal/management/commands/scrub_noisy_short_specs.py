from django.core.management.base import BaseCommand

from portal.models import CatalogItem


SPEC_FIELDS = ("short_specs", "short_specs_ru", "short_specs_en")


class Command(BaseCommand):
    help = "Physically remove noisy scraped pairs from short_specs JSON fields."

    def handle(self, *args, **options):
        updated = 0

        for item in CatalogItem.objects.all():
            changed_fields = []
            for field in SPEC_FIELDS:
                value = getattr(item, field) or {}
                cleaned = dict(item.clean_spec_items(value))
                if cleaned != value:
                    setattr(item, field, cleaned)
                    changed_fields.append(field)
            if changed_fields:
                item.save(update_fields=changed_fields)
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Cleaned short_specs for {updated} items"))
