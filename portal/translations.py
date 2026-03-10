from urllib.parse import urlsplit, urlunsplit
import re


SUPPORTED_LANGUAGES = {"en", "ru", "uk"}

UI_TEXT = {
    "site_name": {"en": "Tech Portal", "ru": "РўРµС…РЅРѕ РџРѕСЂС‚Р°Р»", "uk": "РўРµС…РЅРѕ РџРѕСЂС‚Р°Р»"},
    "site_tagline": {
        "en": "Daily insights for smarter tech choices",
        "ru": "Р•Р¶РµРґРЅРµРІРЅС‹Рµ РјР°С‚РµСЂРёР°Р»С‹ РґР»СЏ СЂР°Р·СѓРјРЅРѕРіРѕ РІС‹Р±РѕСЂР° С‚РµС…РЅРёРєРё",
        "uk": "Р©РѕРґРµРЅРЅС– РјР°С‚РµСЂС–Р°Р»Рё РґР»СЏ СЂРѕР·СѓРјРЅРѕРіРѕ РІРёР±РѕСЂСѓ С‚РµС…РЅС–РєРё",
    },
    "home": {"en": "Home", "ru": "Р“Р»Р°РІРЅР°СЏ", "uk": "Р“РѕР»РѕРІРЅР°"},
    "home_intro": {
        "en": "News, articles, and repair guides in one portal.",
        "ru": "РќРѕРІРѕСЃС‚Рё, СЃС‚Р°С‚СЊРё Рё СЃРїСЂР°РІРѕС‡РЅРёРє РїРѕ СЂРµРјРѕРЅС‚Сѓ РІ РѕРґРЅРѕРј РїРѕСЂС‚Р°Р»Рµ.",
        "uk": "РќРѕРІРёРЅРё, СЃС‚Р°С‚С‚С– С‚Р° РґРѕРІС–РґРЅРёРє Р· СЂРµРјРѕРЅС‚Сѓ РІ РѕРґРЅРѕРјСѓ РїРѕСЂС‚Р°Р»С–.",
    },
    "search": {"en": "Search", "ru": "РџРѕРёСЃРє", "uk": "РџРѕС€СѓРє"},
    "search_description": {
        "en": "Search across articles and repair error guides.",
        "ru": "РС‰РёС‚Рµ РїРѕ СЃС‚Р°С‚СЊСЏРј Рё РёРЅСЃС‚СЂСѓРєС†РёСЏРј РїРѕ СЂРµРјРѕРЅС‚Сѓ.",
        "uk": "РЁСѓРєР°Р№С‚Рµ СЃРµСЂРµРґ СЃС‚Р°С‚РµР№ С‚Р° С–РЅСЃС‚СЂСѓРєС†С–Р№ Р· СЂРµРјРѕРЅС‚Сѓ.",
    },
    "popular_articles": {
        "en": "Popular articles",
        "ru": "РџРѕРїСѓР»СЏСЂРЅС‹Рµ СЃС‚Р°С‚СЊРё",
        "uk": "РџРѕРїСѓР»СЏСЂРЅС– СЃС‚Р°С‚С‚С–",
    },
    "related_articles": {
        "en": "Related articles",
        "ru": "РџРѕС…РѕР¶РёРµ СЃС‚Р°С‚СЊРё",
        "uk": "РЎС…РѕР¶С– СЃС‚Р°С‚С‚С–",
    },
    "latest_articles": {
        "en": "Latest articles",
        "ru": "РЎРІРµР¶РёРµ СЃС‚Р°С‚СЊРё",
        "uk": "РЎРІС–Р¶С– СЃС‚Р°С‚С‚С–",
    },
    "articles": {
        "en": "Articles",
        "ru": "РЎС‚Р°С‚СЊРё",
        "uk": "РЎС‚Р°С‚С‚С–",
    },
    "latest_error_codes": {
        "en": "Repair solutions",
        "ru": "Р РµС€РµРЅРёСЏ РїРѕ СЂРµРјРѕРЅС‚Сѓ",
        "uk": "Р С–С€РµРЅРЅСЏ Р· СЂРµРјРѕРЅС‚Сѓ",
    },
    "error_type_heading": {
        "en": "Choose an appliance type",
        "ru": "Р’С‹Р±РµСЂРёС‚Рµ С‚РёРї С‚РµС…РЅРёРєРё",
        "uk": "РћР±РµСЂС–С‚СЊ С‚РёРї С‚РµС…РЅС–РєРё",
    },
    "error_type_intro": {
        "en": "Start with the appliance type, then choose the brand and the exact model.",
        "ru": "РќР°С‡РЅРёС‚Рµ СЃ С‚РёРїР° С‚РµС…РЅРёРєРё, Р·Р°С‚РµРј РІС‹Р±РµСЂРёС‚Рµ Р±СЂРµРЅРґ Рё РєРѕРЅРєСЂРµС‚РЅСѓСЋ РјРѕРґРµР»СЊ.",
        "uk": "РџРѕС‡РЅС–С‚СЊ Р· С‚РёРїСѓ С‚РµС…РЅС–РєРё, РїРѕС‚С–Рј РѕР±РµСЂС–С‚СЊ Р±СЂРµРЅРґ С– РєРѕРЅРєСЂРµС‚РЅСѓ РјРѕРґРµР»СЊ.",
    },
    "error_brand_intro": {
        "en": "Now choose the brand for this appliance type.",
        "ru": "РўРµРїРµСЂСЊ РІС‹Р±РµСЂРёС‚Рµ Р±СЂРµРЅРґ РґР»СЏ СЌС‚РѕРіРѕ С‚РёРїР° С‚РµС…РЅРёРєРё.",
        "uk": "РўРµРїРµСЂ РѕР±РµСЂС–С‚СЊ Р±СЂРµРЅРґ РґР»СЏ С†СЊРѕРіРѕ С‚РёРїСѓ С‚РµС…РЅС–РєРё.",
    },
    "error_model_intro": {
        "en": "Choose the exact model to open its repair errors and fixes.",
        "ru": "Р’С‹Р±РµСЂРёС‚Рµ С‚РѕС‡РЅСѓСЋ РјРѕРґРµР»СЊ, С‡С‚РѕР±С‹ РѕС‚РєСЂС‹С‚СЊ РѕС€РёР±РєРё Рё СЃРїРѕСЃРѕР±С‹ СЂРµРјРѕРЅС‚Р°.",
        "uk": "РћР±РµСЂС–С‚СЊ С‚РѕС‡РЅСѓ РјРѕРґРµР»СЊ, С‰РѕР± РІС–РґРєСЂРёС‚Рё РїРѕРјРёР»РєРё С‚Р° СЃРїРѕСЃРѕР±Рё СЂРµРјРѕРЅС‚Сѓ.",
    },
    "error_code_list_intro": {
        "en": "Available issues, codes, and repair steps for this model.",
        "ru": "Р”РѕСЃС‚СѓРїРЅС‹Рµ РѕС€РёР±РєРё, РїРѕР»РѕРјРєРё Рё С€Р°РіРё СЂРµРјРѕРЅС‚Р° РґР»СЏ СЌС‚РѕР№ РјРѕРґРµР»Рё.",
        "uk": "Р”РѕСЃС‚СѓРїРЅС– РїРѕРјРёР»РєРё, РїРѕР»РѕРјРєРё С‚Р° РєСЂРѕРєРё СЂРµРјРѕРЅС‚Сѓ РґР»СЏ С†С–С”С— РјРѕРґРµР»С–.",
    },
    "read_more": {"en": "Read more", "ru": "Р§РёС‚Р°С‚СЊ РґР°Р»РµРµ", "uk": "Р§РёС‚Р°С‚Рё РґР°Р»С–"},
    "ad_slot": {"en": "Ad slot", "ru": "Р РµРєР»Р°РјРЅС‹Р№ Р±Р»РѕРє", "uk": "Р РµРєР»Р°РјРЅРёР№ Р±Р»РѕРє"},
    "ad_start": {
        "en": "Google AdSense block at article start",
        "ru": "Р‘Р»РѕРє Google AdSense РІ РЅР°С‡Р°Р»Рµ СЃС‚Р°С‚СЊРё",
        "uk": "Р‘Р»РѕРє Google AdSense РЅР° РїРѕС‡Р°С‚РєСѓ СЃС‚Р°С‚С‚С–",
    },
    "ad_middle": {
        "en": "Google AdSense block in article middle",
        "ru": "Р‘Р»РѕРє Google AdSense РІ СЃРµСЂРµРґРёРЅРµ СЃС‚Р°С‚СЊРё",
        "uk": "Р‘Р»РѕРє Google AdSense РІСЃРµСЂРµРґРёРЅС– СЃС‚Р°С‚С‚С–",
    },
    "ad_end": {
        "en": "Google AdSense block at article end",
        "ru": "Р‘Р»РѕРє Google AdSense РІ РєРѕРЅС†Рµ СЃС‚Р°С‚СЊРё",
        "uk": "Р‘Р»РѕРє Google AdSense РІ РєС–РЅС†С– СЃС‚Р°С‚С‚С–",
    },
    "ad_sidebar": {
        "en": "Google AdSense sidebar block",
        "ru": "Р‘РѕРєРѕРІРѕР№ Р±Р»РѕРє Google AdSense",
        "uk": "Р‘РѕРєРѕРІРёР№ Р±Р»РѕРє Google AdSense",
    },
    "devices": {"en": "Devices", "ru": "РЈСЃС‚СЂРѕР№СЃС‚РІР°", "uk": "РџСЂРёСЃС‚СЂРѕС—"},
    "error_codes": {"en": "Error codes", "ru": "РљРѕРґС‹ РѕС€РёР±РѕРє", "uk": "РљРѕРґРё РїРѕРјРёР»РѕРє"},
    "search_results": {
        "en": "Search results",
        "ru": "Р РµР·СѓР»СЊС‚Р°С‚С‹ РїРѕРёСЃРєР°",
        "uk": "Р РµР·СѓР»СЊС‚Р°С‚Рё РїРѕС€СѓРєСѓ",
    },
    "no_results": {
        "en": "No results found yet.",
        "ru": "РџРѕРєР° РЅРёС‡РµРіРѕ РЅРµ РЅР°Р№РґРµРЅРѕ.",
        "uk": "РџРѕРєРё РЅС–С‡РѕРіРѕ РЅРµ Р·РЅР°Р№РґРµРЅРѕ.",
    },
    "search_placeholder": {
        "en": "Search articles or repair errors",
        "ru": "РСЃРєР°С‚СЊ СЃС‚Р°С‚СЊРё РёР»Рё РѕС€РёР±РєРё СЂРµРјРѕРЅС‚Р°",
        "uk": "РЁСѓРєР°С‚Рё СЃС‚Р°С‚С‚С– Р°Р±Рѕ РїРѕРјРёР»РєРё СЂРµРјРѕРЅС‚Сѓ",
    },
    "footer_note": {
        "en": "Built for scalable SEO publishing on Django.",
        "ru": "РЎРѕР·РґР°РЅРѕ РґР»СЏ РјР°СЃС€С‚Р°Р±РёСЂСѓРµРјРѕР№ SEO-РїСѓР±Р»РёРєР°С†РёРё РЅР° Django.",
        "uk": "РЎС‚РІРѕСЂРµРЅРѕ РґР»СЏ РјР°СЃС€С‚Р°Р±РѕРІР°РЅРѕС— SEO-РїСѓР±Р»С–РєР°С†С–С— РЅР° Django.",
    },
    "published": {"en": "Published", "ru": "РћРїСѓР±Р»РёРєРѕРІР°РЅРѕ", "uk": "РћРїСѓР±Р»С–РєРѕРІР°РЅРѕ"},
    "updated": {"en": "Updated", "ru": "РћР±РЅРѕРІР»РµРЅРѕ", "uk": "РћРЅРѕРІР»РµРЅРѕ"},
    "views": {"en": "Views", "ru": "РџСЂРѕСЃРјРѕС‚СЂС‹", "uk": "РџРµСЂРµРіР»СЏРґРё"},
    "causes": {"en": "Common causes", "ru": "Р§Р°СЃС‚С‹Рµ РїСЂРёС‡РёРЅС‹", "uk": "РџРѕС€РёСЂРµРЅС– РїСЂРёС‡РёРЅРё"},
    "solutions": {"en": "How to fix it", "ru": "РљР°Рє РёСЃРїСЂР°РІРёС‚СЊ", "uk": "РЇРє РІРёРїСЂР°РІРёС‚Рё"},
    "products": {"en": "Products", "ru": "РўРѕРІР°СЂС‹", "uk": "РўРѕРІР°СЂРё"},
    "latest_products": {"en": "Latest products", "ru": "РџРѕСЃР»РµРґРЅРёРµ С‚РѕРІР°СЂС‹", "uk": "РћСЃС‚Р°РЅРЅС– С‚РѕРІР°СЂРё"},
    "catalog_sections": {"en": "Catalog sections", "ru": "Р Р°Р·РґРµР»С‹ РєР°С‚Р°Р»РѕРіР°", "uk": "Р РѕР·РґС–Р»Рё РєР°С‚Р°Р»РѕРіСѓ"},
    "items_in_section": {"en": "items", "ru": "С‚РѕРІР°СЂРѕРІ", "uk": "С‚РѕРІР°СЂС–РІ"},
    "brands": {"en": "Brands", "ru": "Р‘СЂРµРЅРґС‹", "uk": "Р‘СЂРµРЅРґРё"},
    "filters": {"en": "Filters", "ru": "Р¤РёР»СЊС‚СЂС‹", "uk": "Р¤С–Р»СЊС‚СЂРё"},
    "apply_filters": {"en": "Apply", "ru": "РџСЂРёРјРµРЅРёС‚СЊ", "uk": "Р—Р°СЃС‚РѕСЃСѓРІР°С‚Рё"},
    "reset_filters": {"en": "Reset", "ru": "РЎР±СЂРѕСЃРёС‚СЊ", "uk": "РЎРєРёРЅСѓС‚Рё"},
    "product_catalog_intro": {
        "en": "Catalog of parsed appliance models with specs, repair codes, and common faults.",
        "ru": "РљР°С‚Р°Р»РѕРі СЂР°СЃРїР°СЂСЃРµРЅРЅС‹С… РјРѕРґРµР»РµР№ СЃ С…Р°СЂР°РєС‚РµСЂРёСЃС‚РёРєР°РјРё, РєРѕРґР°РјРё РѕС€РёР±РѕРє Рё С‚РёРїРѕРІС‹РјРё РЅРµРёСЃРїСЂР°РІРЅРѕСЃС‚СЏРјРё.",
        "uk": "РљР°С‚Р°Р»РѕРі СЂРѕР·РїР°СЂСЃРµРЅРёС… РјРѕРґРµР»РµР№ Р· С…Р°СЂР°РєС‚РµСЂРёСЃС‚РёРєР°РјРё, РєРѕРґР°РјРё РїРѕРјРёР»РѕРє С– С‚РёРїРѕРІРёРјРё РЅРµСЃРїСЂР°РІРЅРѕСЃС‚СЏРјРё.",
    },
    "common_faults": {"en": "Common faults", "ru": "РўРёРїРѕРІС‹Рµ РЅРµРёСЃРїСЂР°РІРЅРѕСЃС‚Рё", "uk": "РўРёРїРѕРІС– РЅРµСЃРїСЂР°РІРЅРѕСЃС‚С–"},
    "repair_tips": {"en": "Repair tips", "ru": "РЎРѕРІРµС‚С‹ РїРѕ СЂРµРјРѕРЅС‚Сѓ", "uk": "РџРѕСЂР°РґРё Р· СЂРµРјРѕРЅС‚Сѓ"},
    "full_description": {"en": "Full description", "ru": "Полное описание", "uk": "Повний опис"},
    "additional_notes": {"en": "Additional notes", "ru": "Дополнительные заметки", "uk": "Додаткові нотатки"},
    "short_specs": {"en": "Short specs", "ru": "РљСЂР°С‚РєРёРµ С…Р°СЂР°РєС‚РµСЂРёСЃС‚РёРєРё", "uk": "РљРѕСЂРѕС‚РєС– С…Р°СЂР°РєС‚РµСЂРёСЃС‚РёРєРё"},
    "helpful_links": {"en": "Helpful links", "ru": "РџРѕР»РµР·РЅС‹Рµ СЃСЃС‹Р»РєРё", "uk": "РљРѕСЂРёСЃРЅС– РїРѕСЃРёР»Р°РЅРЅСЏ"},
    "sources": {"en": "Sources", "ru": "РСЃС‚РѕС‡РЅРёРєРё", "uk": "Р”Р¶РµСЂРµР»Р°"},
    "similar_products": {"en": "Similar products", "ru": "РџРѕС…РѕР¶РёРµ С‚РѕРІР°СЂС‹", "uk": "РЎС…РѕР¶С– С‚РѕРІР°СЂРё"},
    "product_page": {"en": "Product page", "ru": "РЎС‚СЂР°РЅРёС†Р° С‚РѕРІР°СЂР°", "uk": "РЎС‚РѕСЂС–РЅРєР° С‚РѕРІР°СЂСѓ"},
    "first_checks": {"en": "First checks", "ru": "РџРµСЂРІС‹Рµ РїСЂРѕРІРµСЂРєРё", "uk": "РџРµСЂС€С– РїРµСЂРµРІС–СЂРєРё"},
    "likely_causes": {"en": "Likely causes", "ru": "Р’РµСЂРѕСЏС‚РЅС‹Рµ РїСЂРёС‡РёРЅС‹", "uk": "Р™РјРѕРІС–СЂРЅС– РїСЂРёС‡РёРЅРё"},
    "search_links": {"en": "Search links", "ru": "РџРѕРёСЃРєРѕРІС‹Рµ СЃСЃС‹Р»РєРё", "uk": "РџРѕС€СѓРєРѕРІС– РїРѕСЃРёР»Р°РЅРЅСЏ"},
    "coverage": {"en": "Coverage", "ru": "РџРѕРєСЂС‹С‚РёРµ", "uk": "РџРѕРєСЂРёС‚С‚СЏ"},
    "brand": {"en": "Brand", "ru": "Р‘СЂРµРЅРґ", "uk": "Р‘СЂРµРЅРґ"},
    "model": {"en": "Model", "ru": "РњРѕРґРµР»СЊ", "uk": "РњРѕРґРµР»СЊ"},
}


CATEGORY_LABELS = {}
CATEGORY_DESCRIPTIONS = {}

UI_TEXT_OVERRIDES = {
    "search": {"en": "Search", "ru": "Поиск", "uk": "Пошук"},
    "search_placeholder": {
        "en": "Search articles or repair errors",
        "ru": "Искать статьи или ошибки ремонта",
        "uk": "Шукати статті або помилки ремонту",
    },
    "description": {"en": "Description", "ru": "Описание", "uk": "Опис"},
    "views": {"en": "Views", "ru": "Просмотры", "uk": "Перегляди"},
    "common_faults": {"en": "Common faults", "ru": "Типовые неисправности", "uk": "Типові несправності"},
    "repair_tips": {"en": "Repair tips", "ru": "Советы по ремонту", "uk": "Поради з ремонту"},
    "short_specs": {"en": "Short specs", "ru": "Краткие характеристики", "uk": "Короткі характеристики"},
    "full_description": {"en": "Full description", "ru": "Полное описание", "uk": "Повний опис"},
    "additional_notes": {"en": "Additional notes", "ru": "Дополнительные заметки", "uk": "Додаткові нотатки"},
    "helpful_links": {"en": "Helpful links", "ru": "Полезные ссылки", "uk": "Корисні посилання"},
    "sources": {"en": "Sources", "ru": "Источники", "uk": "Джерела"},
    "search_links": {"en": "Search links", "ru": "Поисковые ссылки", "uk": "Пошукові посилання"},
    "coverage": {"en": "Coverage", "ru": "Покрытие", "uk": "Покриття"},
    "product_page": {"en": "Product page", "ru": "Страница товара", "uk": "Сторінка товару"},
    "first_checks": {"en": "First checks", "ru": "Первые проверки", "uk": "Перші перевірки"},
    "likely_causes": {"en": "Likely causes", "ru": "Вероятные причины", "uk": "Ймовірні причини"},
}

MOJIBAKE_RE = re.compile(r"[РСІЇЄҐЃ][^\s]{0,2}")


def maybe_fix_mojibake(value):
    if not isinstance(value, str) or not value:
        return value
    if not MOJIBAKE_RE.search(value):
        return value
    try:
        fixed = value.encode("cp1251", errors="strict").decode("utf-8", errors="strict")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value

    original_score = sum(char.isalpha() for char in value)
    fixed_cyrillic_score = sum("\u0400" <= char <= "\u04FF" for char in fixed)
    mojibake_markers = fixed.count("Р") + fixed.count("С")
    if fixed_cyrillic_score >= max(3, original_score // 3) and mojibake_markers < (value.count("Р") + value.count("С")):
        return fixed
    return value


def get_text(key, language="uk"):
    language = (language or "uk")[:2]
    translation_map = UI_TEXT_OVERRIDES.get(key) or UI_TEXT.get(key, {})
    result = (
        translation_map.get(language)
        or translation_map.get("uk")
        or translation_map.get("en")
        or key.replace("_", " ").title()
    )
    return maybe_fix_mojibake(result)


def get_category_label(slug, language="uk"):
    language = (language or "uk")[:2]
    labels = CATEGORY_LABELS.get(slug, {})
    result = labels.get(language) or labels.get("uk") or labels.get("en") or slug.replace("-", " ").title()
    return maybe_fix_mojibake(result)


def get_category_description(slug, language="uk"):
    language = (language or "uk")[:2]
    descriptions = CATEGORY_DESCRIPTIONS.get(slug, {})
    result = descriptions.get(language) or descriptions.get("uk") or descriptions.get("en") or ""
    return maybe_fix_mojibake(result)


def localized_path(full_path, target_language):
    parts = urlsplit(full_path or "/")
    segments = parts.path.split("/")
    if len(segments) > 1 and segments[1] in SUPPORTED_LANGUAGES:
        segments[1] = target_language
        new_path = "/".join(segments)
    else:
        path = parts.path if parts.path.startswith("/") else f"/{parts.path}"
        new_path = f"/{target_language}{path}"
    if not new_path.endswith("/") and parts.path.endswith("/"):
        new_path = f"{new_path}/"
    return urlunsplit(("", "", new_path, parts.query, parts.fragment))
