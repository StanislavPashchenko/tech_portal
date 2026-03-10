from django.core.management.base import BaseCommand

from portal.models import CatalogItem


DESCRIPTION_FIELDS = (
    ("uk", "product_description"),
    ("ru", "product_description_ru"),
    ("en", "product_description_en"),
)


class Command(BaseCommand):
    help = "Generate localized product descriptions for empty or generic catalog items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--only-generic",
            action="store_true",
            help="Update only descriptions that match generic E-Katalog boilerplate.",
        )

    def handle(self, *args, **options):
        updated_items = 0
        updated_fields = 0

        for item in CatalogItem.objects.select_related(
            "repair_model",
            "repair_model__repair_brand",
            "repair_model__repair_brand__appliance_type",
        ):
            changed_fields = []
            for language, field_name in DESCRIPTION_FIELDS:
                current_value = getattr(item, field_name) or ""
                cleaned_value = item.clean_product_description(current_value)
                is_generic = item.is_generic_product_description(cleaned_value, language)

                if options["only_generic"] and not is_generic:
                    continue
                if not options["only_generic"] and cleaned_value and not is_generic:
                    continue

                generated = item.generate_product_description(language)
                if not generated or generated == current_value:
                    continue

                setattr(item, field_name, generated)
                changed_fields.append(field_name)

            if changed_fields:
                item.save(update_fields=changed_fields)
                updated_items += 1
                updated_fields += len(changed_fields)

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated descriptions for {updated_items} items across {updated_fields} localized fields."
            )
        )
