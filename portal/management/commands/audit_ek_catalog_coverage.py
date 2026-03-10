import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand

from portal.models import CatalogItem


LANGUAGE_FILE_MAP = {"uk": "ua", "ru": "ru", "en": "en"}
LANGUAGE_LABEL_MAP = {"uk": "ua", "ru": "ru", "en": "en"}
SOURCE_ROOTS = {
    "washing-machines": "models_cat91_full",
    "refrigerators": "models_trilang_full",
}


def normalize_url(url):
    if not url:
        return ""
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}{path}" if parsed.scheme and parsed.netloc else url.strip().rstrip("/")


def flatten_specs(data):
    raw_specs = data.get("raw_specs") or {}
    flattened = {}
    if not isinstance(raw_specs, dict):
        return flattened
    for group_specs in raw_specs.values():
        if not isinstance(group_specs, dict):
            continue
        for label, value in group_specs.items():
            flattened[str(label)] = str(value)
    return flattened


class Command(BaseCommand):
    help = "Compare catalog items against local E-Katalog snapshots and report missing data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=str(settings.BASE_DIR / "ek_catalog_missing_report.json"),
            help="Path to the JSON audit report.",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"])
        source_index = self.build_source_index()
        report = self.build_report(source_index)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        summary = report["summary"]
        self.stdout.write(self.style.SUCCESS(f"Saved report to {output_path}"))
        self.stdout.write(
            f"Items checked: {summary['total_items']} | "
            f"matched with source: {summary['matched_items']} | "
            f"without source snapshot: {summary['items_without_source_snapshot']} | "
            f"with missing specs: {summary['items_with_missing_specs']} | "
            f"with missing descriptions: {summary['items_with_missing_descriptions']}"
        )

    def build_source_index(self):
        source_index = {}
        for appliance_slug, root_name in SOURCE_ROOTS.items():
            root = settings.BASE_DIR / root_name
            if not root.exists():
                continue
            for model_dir in sorted(path for path in root.iterdir() if path.is_dir()):
                for db_language, file_language in LANGUAGE_FILE_MAP.items():
                    file_path = model_dir / f"{file_language}.json"
                    if not file_path.exists():
                        continue
                    data = json.loads(file_path.read_text(encoding="utf-8"))
                    url = normalize_url(
                        (data.get("source") or {}).get("actual_url") or (data.get("source") or {}).get("url") or ""
                    )
                    if not url:
                        continue
                    description = CatalogItem.clean_product_description(data.get("description") or "")
                    if CatalogItem.is_generic_product_description(description, db_language):
                        description = ""
                    source_index[(appliance_slug, db_language, url)] = {
                        "specs": dict(CatalogItem.clean_spec_items(flatten_specs(data))),
                        "description": description,
                        "images_count": len(data.get("images") or []),
                        "folder": model_dir.name,
                    }
        return source_index

    def build_report(self, source_index):
        summary = {
            "total_items": 0,
            "matched_items": 0,
            "items_without_source_snapshot": 0,
            "items_with_missing_specs": 0,
            "items_with_missing_descriptions": 0,
            "items_with_missing_images": 0,
        }
        top_missing_keys = defaultdict(Counter)
        detailed_items = []

        queryset = CatalogItem.objects.select_related(
            "repair_model__repair_brand__appliance_type",
            "repair_model__repair_brand",
        ).order_by("id")

        for item in queryset:
            appliance_slug = item.repair_model.repair_brand.appliance_type.slug
            if appliance_slug not in SOURCE_ROOTS:
                continue

            summary["total_items"] += 1
            item_report = {
                "id": item.id,
                "appliance_type": appliance_slug,
                "brand": item.repair_model.repair_brand.name_en or item.repair_model.repair_brand.name,
                "model": item.repair_model.name_en or item.repair_model.name,
                "slug": item.repair_model.slug,
                "source_url": item.source_url,
                "languages": {},
            }
            item_has_missing_specs = False
            item_has_missing_description = False
            item_has_missing_images = False
            item_matched = False

            for language in ("uk", "ru", "en"):
                source_url = normalize_url((item.model_search_urls or {}).get(language) or item.source_url)
                source_entry = source_index.get((appliance_slug, language, source_url))
                db_specs = item.get_clean_specs(language)
                db_description = CatalogItem.clean_product_description(
                    item.get_localized_value("product_description", language) or ""
                )
                db_description_is_real = bool(db_description) and not CatalogItem.is_generic_product_description(
                    db_description, language
                )

                language_report = {
                    "source_url": source_url,
                    "source_found": bool(source_entry),
                    "missing_spec_keys": [],
                    "missing_description": False,
                    "missing_images": False,
                }

                if not source_entry:
                    item_report["languages"][language] = language_report
                    continue

                item_matched = True
                missing_spec_keys = [key for key in source_entry["specs"] if key not in db_specs]
                if missing_spec_keys:
                    language_report["missing_spec_keys"] = missing_spec_keys
                    item_has_missing_specs = True
                    for key in missing_spec_keys:
                        top_missing_keys[(appliance_slug, language)][key] += 1

                if source_entry["description"] and not db_description_is_real:
                    language_report["missing_description"] = True
                    item_has_missing_description = True

                image_count = item.images.count()
                if source_entry["images_count"] and image_count < source_entry["images_count"]:
                    language_report["missing_images"] = True
                    language_report["source_images_count"] = source_entry["images_count"]
                    language_report["catalog_images_count"] = image_count
                    item_has_missing_images = True

                item_report["languages"][language] = language_report

            if item_matched:
                summary["matched_items"] += 1
            else:
                summary["items_without_source_snapshot"] += 1

            if item_has_missing_specs:
                summary["items_with_missing_specs"] += 1
            if item_has_missing_description:
                summary["items_with_missing_descriptions"] += 1
            if item_has_missing_images:
                summary["items_with_missing_images"] += 1

            if item_has_missing_specs or item_has_missing_description or item_has_missing_images or not item_matched:
                detailed_items.append(item_report)

        top_missing_keys_report = {}
        for (appliance_slug, language), counter in top_missing_keys.items():
            top_missing_keys_report.setdefault(appliance_slug, {})[language] = counter.most_common(30)

        return {
            "summary": summary,
            "top_missing_keys": top_missing_keys_report,
            "items": detailed_items,
        }
