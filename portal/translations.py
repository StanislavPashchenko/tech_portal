from urllib.parse import urlsplit, urlunsplit


SUPPORTED_LANGUAGES = {"en", "ru", "uk"}

UI_TEXT = {
    "site_name": {
        "en": "Tech Portal",
        "ru": "Техно Портал",
        "uk": "Техно Портал",
    },
    "site_tagline": {
        "en": "Daily insights for smarter tech choices",
        "ru": "Ежедневные материалы для разумного выбора техники",
        "uk": "Щоденні матеріали для розумного вибору техніки",
    },
    "home": {"en": "Home", "ru": "Главная", "uk": "Головна"},
    "home_intro": {
        "en": "News, reviews, comparisons, practical guides, and appliance error fixes in one portal.",
        "ru": "Новости, обзоры, сравнения, инструкции и решения ошибок бытовой техники в одном портале.",
        "uk": "Новини, огляди, порівняння, інструкції та рішення помилок техніки в одному порталі.",
    },
    "categories": {"en": "Categories", "ru": "Категории", "uk": "Категорії"},
    "categories_description": {
        "en": "Browse technology content by editorial category.",
        "ru": "Просматривайте технологические материалы по редакционным категориям.",
        "uk": "Переглядайте технологічні матеріали за редакційними категоріями.",
    },
    "brands": {"en": "Brands", "ru": "Бренды", "uk": "Бренди"},
    "brands_description": {
        "en": "Brand hubs with articles, devices, and error codes.",
        "ru": "Страницы брендов со статьями, устройствами и кодами ошибок.",
        "uk": "Сторінки брендів зі статтями, пристроями та кодами помилок.",
    },
    "search": {"en": "Search", "ru": "Поиск", "uk": "Пошук"},
    "search_description": {
        "en": "Search across tech articles and appliance error code guides.",
        "ru": "Ищите по технологическим статьям и инструкциям по кодам ошибок.",
        "uk": "Шукайте серед технологічних статей і довідників з кодів помилок.",
    },
    "popular_articles": {
        "en": "Popular articles",
        "ru": "Популярные статьи",
        "uk": "Популярні статті",
    },
    "related_articles": {
        "en": "Related articles",
        "ru": "Похожие статьи",
        "uk": "Схожі статті",
    },
    "latest_error_codes": {
        "en": "Error code solutions",
        "ru": "Решения кодов ошибок",
        "uk": "Рішення кодів помилок",
    },
    "read_more": {"en": "Read more", "ru": "Читать далее", "uk": "Читати далі"},
    "view_brand": {"en": "View brand", "ru": "Страница бренда", "uk": "Сторінка бренду"},
    "all_categories": {
        "en": "All categories",
        "ru": "Все категории",
        "uk": "Усі категорії",
    },
    "all_brands": {"en": "All brands", "ru": "Все бренды", "uk": "Усі бренди"},
    "latest_articles": {
        "en": "Latest articles",
        "ru": "Свежие статьи",
        "uk": "Свіжі статті",
    },
    "top_brands": {"en": "Top brands", "ru": "Популярные бренды", "uk": "Популярні бренди"},
    "ad_slot": {"en": "Ad slot", "ru": "Рекламный блок", "uk": "Рекламний блок"},
    "ad_start": {
        "en": "Google AdSense block at article start",
        "ru": "Блок Google AdSense в начале статьи",
        "uk": "Блок Google AdSense на початку статті",
    },
    "ad_middle": {
        "en": "Google AdSense block in article middle",
        "ru": "Блок Google AdSense в середине статьи",
        "uk": "Блок Google AdSense всередині статті",
    },
    "ad_end": {
        "en": "Google AdSense block at article end",
        "ru": "Блок Google AdSense в конце статьи",
        "uk": "Блок Google AdSense в кінці статті",
    },
    "ad_sidebar": {
        "en": "Google AdSense sidebar block",
        "ru": "Боковой блок Google AdSense",
        "uk": "Боковий блок Google AdSense",
    },
    "devices": {"en": "Devices", "ru": "Устройства", "uk": "Пристрої"},
    "error_codes": {"en": "Error codes", "ru": "Коды ошибок", "uk": "Коди помилок"},
    "search_results": {
        "en": "Search results",
        "ru": "Результаты поиска",
        "uk": "Результати пошуку",
    },
    "no_results": {
        "en": "No results found yet.",
        "ru": "Пока ничего не найдено.",
        "uk": "Поки нічого не знайдено.",
    },
    "search_placeholder": {
        "en": "Search articles or error codes",
        "ru": "Искать статьи или коды ошибок",
        "uk": "Шукати статті або коди помилок",
    },
    "footer_note": {
        "en": "Built for scalable SEO publishing on Django.",
        "ru": "Создано для масштабируемой SEO-публикации на Django.",
        "uk": "Створено для масштабованої SEO-публікації на Django.",
    },
    "published": {"en": "Published", "ru": "Опубликовано", "uk": "Опубліковано"},
    "updated": {"en": "Updated", "ru": "Обновлено", "uk": "Оновлено"},
    "views": {"en": "Views", "ru": "Просмотры", "uk": "Перегляди"},
    "causes": {"en": "Common causes", "ru": "Частые причины", "uk": "Поширені причини"},
    "solutions": {"en": "How to fix it", "ru": "Как исправить", "uk": "Як виправити"},
}

CATEGORY_LABELS = {
    "news": {"en": "Tech News", "ru": "Новости техники", "uk": "Новини техніки"},
    "reviews": {"en": "Device Reviews", "ru": "Обзоры устройств", "uk": "Огляди пристроїв"},
    "comparisons": {"en": "Comparisons", "ru": "Сравнения техники", "uk": "Порівняння техніки"},
    "guides": {"en": "Guides & Tips", "ru": "Инструкции и советы", "uk": "Інструкції та поради"},
    "errors": {"en": "Error Codes", "ru": "Коды ошибок техники", "uk": "Коди помилок техніки"},
}

CATEGORY_DESCRIPTIONS = {
    "news": {
        "en": "Latest updates from the consumer tech and smart home market.",
        "ru": "Последние события рынка потребительской электроники и умного дома.",
        "uk": "Останні події ринку споживчої електроніки та розумного дому.",
    },
    "reviews": {
        "en": "Hands-on reviews, buying advice, and verdicts for popular gadgets.",
        "ru": "Практические обзоры, советы по покупке и выводы по популярной технике.",
        "uk": "Практичні огляди, поради з покупки та висновки щодо популярної техніки.",
    },
    "comparisons": {
        "en": "Head-to-head product comparisons to help users choose the best device.",
        "ru": "Сравнения устройств лицом к лицу, помогающие выбрать лучший вариант.",
        "uk": "Порівняння пристроїв, які допомагають вибрати найкращий варіант.",
    },
    "guides": {
        "en": "Step-by-step instructions, maintenance tips, and troubleshooting advice.",
        "ru": "Пошаговые инструкции, советы по уходу и рекомендации по устранению проблем.",
        "uk": "Покрокові інструкції, поради з догляду та рекомендації з усунення проблем.",
    },
    "errors": {
        "en": "Appliance error code explanations with causes and repair steps.",
        "ru": "Расшифровка кодов ошибок техники с причинами и шагами устранения.",
        "uk": "Розшифрування кодів помилок техніки з причинами та кроками усунення.",
    },
}


def get_text(key, language="uk"):
    language = (language or "uk")[:2]
    translation_map = UI_TEXT.get(key, {})
    return translation_map.get(language) or translation_map.get("uk") or translation_map.get("en") or key.replace("_", " ").title()


def get_category_label(slug, language="uk"):
    language = (language or "uk")[:2]
    labels = CATEGORY_LABELS.get(slug, {})
    return labels.get(language) or labels.get("uk") or labels.get("en") or slug.replace("-", " ").title()


def get_category_description(slug, language="uk"):
    language = (language or "uk")[:2]
    descriptions = CATEGORY_DESCRIPTIONS.get(slug, {})
    return descriptions.get(language) or descriptions.get("uk") or descriptions.get("en") or ""


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
