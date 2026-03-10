import json
import re
from pathlib import Path


DEFAULT_ITEMS_DIR = Path(r"C:\Users\snoby\Desktop\translater\items")
LANGS = ("ru", "en")

SECTION_MAP = {
    "Характеристики": {"ru": "Характеристики", "en": "Specifications"},
    "Функції та можливості": {"ru": "Функции и возможности", "en": "Functions and features"},
    "Безпека": {"ru": "Безопасность", "en": "Safety"},
    "Класи ефективності": {"ru": "Классы эффективности", "en": "Efficiency classes"},
    "Загальні характеристики": {"ru": "Общие характеристики", "en": "General"},
}

SPEC_KEY_MAP = {
    "Тип завантаження": {"ru": "Тип загрузки", "en": "Loading type"},
    "Завантаження": {"ru": "Загрузка", "en": "Load capacity"},
    "Об'єм барабана": {"ru": "Объем барабана", "en": "Drum volume"},
    "Максимальна швидкість віджимання": {"ru": "Максимальная скорость отжима", "en": "Max spin speed"},
    "Витрата води за цикл": {"ru": "Расход воды за цикл", "en": "Water consumption per cycle"},
    "Сушка": {"ru": "Сушка", "en": "Dryer"},
    "Прямий привод двигуна": {"ru": "Прямой привод двигателя", "en": "Direct drive motor"},
    "Завантаження для сушіння": {"ru": "Загрузка для сушки", "en": "Drying load"},
    "Інверторний двигун": {"ru": "Инверторный двигатель", "en": "Inverter motor"},
    "Матеріал бака": {"ru": "Материал бака", "en": "Tub material"},
    "Матеріал ТЕНу": {"ru": "Материал ТЭНа", "en": "Heating element material"},
    "Кількість програм": {"ru": "Количество программ", "en": "Number of programs"},
    "Додаткові програми": {"ru": "Дополнительные программы", "en": "Additional programs"},
    "Прання паром": {"ru": "Стирка паром", "en": "Steam wash"},
    "Таймер закінчення прання": {"ru": "Таймер окончания стирки", "en": "End timer"},
    "Автоматичне дозування": {"ru": "Автоматическая дозировка", "en": "Automatic dosing"},
    "Струминне полоскання": {"ru": "Струйное полоскание", "en": "Jet rinse"},
    "Захист від протікання": {"ru": "Защита от протечек", "en": "Leak protection"},
    "Захист від перепадів напруги": {"ru": "Защита от перепадов напряжения", "en": "Voltage fluctuation protection"},
    "Контроль піноутворення": {"ru": "Контроль пенообразования", "en": "Foam control"},
    "Контроль дисбалансу": {"ru": "Контроль дисбаланса", "en": "Imbalance control"},
    "Захист від дітей": {"ru": "Защита от детей", "en": "Child lock"},
    "Клас віджимання": {"ru": "Класс отжима", "en": "Spin class"},
    "Клас енергоспоживання": {"ru": "Класс энергопотребления", "en": "Energy class"},
    "Клас енергоспоживання (new)": {"ru": "Класс энергопотребления (new)", "en": "Energy class (new)"},
    "Клас гучності": {"ru": "Класс шума", "en": "Noise class"},
    "Управління": {"ru": "Управление", "en": "Controls"},
    "Керування зі смартфона": {"ru": "Управление со смартфона", "en": "Smartphone control"},
    "Дисплей": {"ru": "Дисплей", "en": "Display"},
    "Відкриття дверцят": {"ru": "Открытие дверцы", "en": "Door opening"},
    "Кут відкривання": {"ru": "Угол открытия", "en": "Opening angle"},
    "Рівень шуму (віджимання)": {"ru": "Уровень шума (отжим)", "en": "Noise level (spin)"},
    "Діаметр завантажувального люка": {"ru": "Диаметр загрузочного люка", "en": "Loading hatch diameter"},
    "Габарити (ВхШхГ)": {"ru": "Габариты (ВхШхГ)", "en": "Dimensions (HxWxD)"},
    "Країна виробництва": {"ru": "Страна производства", "en": "Country of origin"},
    "Офіційний сайт": {"ru": "Официальный сайт", "en": "Official site"},
    "Дата додавання на E-Katalog": {"ru": "Дата добавления на E-Katalog", "en": "Added to E-Katalog"},
    "Маркування виробника": {"ru": "Маркировка производителя", "en": "Manufacturer code"},
    "Вага": {"ru": "Вес", "en": "Weight"},
    "Підсвічування барабана": {"ru": "Подсветка барабана", "en": "Drum lighting"},
}

SHORT_SPEC_KEY_MAP = {
    "Прання:": {"ru": "Стирка:", "en": "Wash:"},
    "Сушіння:": {"ru": "Сушка:", "en": "Drying:"},
    "Віджим:": {"ru": "Отжим:", "en": "Spin:"},
    "Програми:": {"ru": "Программы:", "en": "Programs:"},
    "Енергоефективність:": {"ru": "Энергоэффективность:", "en": "Energy efficiency:"},
    "Рівень шуму:": {"ru": "Уровень шума:", "en": "Noise level:"},
    "Глибина пральної машини:": {"ru": "Глубина стиральной машины:", "en": "Washer depth:"},
}

VALUE_MAP = {
    "білий": {"ru": "белый", "en": "white"},
    "чорний": {"ru": "черный", "en": "black"},
    "сірий": {"ru": "серый", "en": "gray"},
    "сріблястий": {"ru": "серебристый", "en": "silver"},
    "фронтальне завантаження": {"ru": "фронтальная загрузка", "en": "front loading"},
    "вертикальне завантаження": {"ru": "вертикальная загрузка", "en": "top loading"},
    "пластик": {"ru": "пластик", "en": "plastic"},
    "нержавіюча сталь": {"ru": "нержавеющая сталь", "en": "stainless steel"},
    "поворотна ручка + сенсори": {"ru": "поворотная ручка + сенсоры", "en": "rotary knob + sensors"},
    "поворотна ручка + кнопки": {"ru": "поворотная ручка + кнопки", "en": "rotary knob + buttons"},
    "поворотна ручка": {"ru": "поворотная ручка", "en": "rotary knob"},
    "сенсорне": {"ru": "сенсорное", "en": "touch"},
    "вліво": {"ru": "влево", "en": "left"},
    "вправо": {"ru": "вправо", "en": "right"},
    "швидке прання": {"ru": "быстрая стирка", "en": "quick wash"},
    "делікатне прання": {"ru": "деликатная стирка", "en": "delicate wash"},
    "гігієна (дитячий одяг)": {"ru": "гигиена (детская одежда)", "en": "hygiene (baby clothes)"},
    "пухові речі": {"ru": "пуховые вещи", "en": "down items"},
    "верхній одяг": {"ru": "верхняя одежда", "en": "outerwear"},
    "спортивний одяг": {"ru": "спортивная одежда", "en": "sportswear"},
    "темний одяг": {"ru": "темная одежда", "en": "dark clothes"},
    "джинсовий одяг": {"ru": "джинсовая одежда", "en": "denim clothes"},
    "сорочки": {"ru": "рубашки", "en": "shirts"},
    "ковдри": {"ru": "одеяла", "en": "blankets"},
    "рушники": {"ru": "полотенца", "en": "towels"},
    "подушки": {"ru": "подушки", "en": "pillows"},
    "постільна білизна": {"ru": "постельное белье", "en": "bed linen"},
    "освіження (без прання)": {"ru": "освежение (без стирки)", "en": "refresh (without wash)"},
    "самоочищення": {"ru": "самоочистка", "en": "self-cleaning"},
    "своя програма": {"ru": "своя программа", "en": "custom program"},
    "прання + сушіння": {"ru": "стирка + сушка", "en": "wash + drying"},
    "14 хвилин": {"ru": "14 минут", "en": "14 min"},
    "15 хвилин": {"ru": "15 минут", "en": "15 min"},
    "30 хвилин": {"ru": "30 минут", "en": "30 min"},
    "39 хвилин": {"ru": "39 минут", "en": "39 min"},
    "44 хвилини": {"ru": "44 минуты", "en": "44 min"},
    "59 хвилин": {"ru": "59 минут", "en": "59 min"},
    "при пранні": {"ru": "при стирке", "en": "during wash"},
    "при віджиманні": {"ru": "при отжиме", "en": "during spin"},
    "квтг/рік": {"ru": "кВтч/год", "en": "kWh/year"},
    "хвиLин": {"ru": "минут", "en": "min"},
    "хвилин": {"ru": "минут", "en": "min"},
    "Китай": {"ru": "Китай", "en": "China"},
    "Туреччина": {"ru": "Турция", "en": "Turkey"},
    "Польща": {"ru": "Польша", "en": "Poland"},
    "ПоLьща": {"ru": "Польша", "en": "Poland"},
    "Німеччина": {"ru": "Германия", "en": "Germany"},
    "Італія": {"ru": "Италия", "en": "Italy"},
    "Словаччина": {"ru": "Словакия", "en": "Slovakia"},
    "Словенія": {"ru": "Словения", "en": "Slovenia"},
    "Україна": {"ru": "Украина", "en": "Ukraine"},
    "ТЕН відсутній": {"ru": "ТЭН отсутствует", "en": "no heating element"},
    "Serie 4": {"ru": "Serie 4", "en": "Serie 4"},
    "Serie 5": {"ru": "Serie 5", "en": "Serie 5"},
    "Serie 6": {"ru": "Serie 6", "en": "Serie 6"},
    "Serie 7": {"ru": "Serie 7", "en": "Serie 7"},
    "Serie 8": {"ru": "Serie 8", "en": "Serie 8"},
    "2023 рік": {"ru": "2023 год", "en": "2023 model year"},
    "2024 рік": {"ru": "2024 год", "en": "2024 model year"},
    "тиха": {"ru": "тихая", "en": "quiet"},
    "з сушкою": {"ru": "с сушкой", "en": "with dryer"},
}

MONTH_MAP = {
    "січень": {"ru": "январь", "en": "January"},
    "лютий": {"ru": "февраль", "en": "February"},
    "березень": {"ru": "март", "en": "March"},
    "квітень": {"ru": "апрель", "en": "April"},
    "травень": {"ru": "май", "en": "May"},
    "червень": {"ru": "июнь", "en": "June"},
    "липень": {"ru": "июль", "en": "July"},
    "серпень": {"ru": "август", "en": "August"},
    "вересень": {"ru": "сентябрь", "en": "September"},
    "жовтень": {"ru": "октябрь", "en": "October"},
    "листопад": {"ru": "ноябрь", "en": "November"},
    "грудень": {"ru": "декабрь", "en": "December"},
}


def translate_url(url: str, lang: str) -> str:
    if not url:
        return ""
    if lang == "ru":
        return url.replace("/ua/", "/").replace("https://ek.ua/ua/", "https://ek.ua/")
    if "https://ek.ua/ua/" in url:
        return url.replace("https://ek.ua/ua/", "https://ek.ua/en/")
    if "https://ek.ua/" in url and "https://ek.ua/en/" not in url:
        return url.replace("https://ek.ua/", "https://ek.ua/en/")
    return url


def translate_months(text: str, lang: str) -> str:
    if lang == "uk":
        return text
    result = text
    for src, mapping in MONTH_MAP.items():
        result = re.sub(rf"\b{re.escape(src)}\b", mapping[lang], result, flags=re.IGNORECASE)
    return result


def translate_scalar(value, lang: str):
    if isinstance(value, bool) or value is None:
        return value
    if not isinstance(value, str):
        return value
    if lang == "uk":
        return value.strip()
    result = translate_months(value, lang)
    for src, mapping in sorted(VALUE_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        result = re.sub(re.escape(src), mapping[lang], result, flags=re.IGNORECASE)
    if lang == "ru":
        result = result.replace("об/хв", "об/мин")
        result = result.replace("кг", "кг")
    else:
        result = result.replace("об/хв", "rpm")
        result = result.replace("дБ", "dB")
        result = result.replace("см", "cm")
        result = result.replace("кг", "kg")
        result = result.replace("л", "L")
        result = result.replace("шт.", "pcs.")
    return result.strip()


def translate_dict(data: dict, key_map: dict, lang: str) -> dict:
    translated = {}
    for key, value in data.items():
        target_key = key_map.get(key, {}).get(lang, key)
        if isinstance(value, dict):
            translated[target_key] = translate_dict(value, key_map, lang)
        elif isinstance(value, list):
            translated[target_key] = [translate_scalar(item, lang) for item in value]
        else:
            translated[target_key] = translate_scalar(value, lang)
    return translated


def get_spec(data: dict, *keys: str) -> str:
    specs = data.get("full_specifications", {}) or {}
    for key in keys:
        value = specs.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def extract_depth(data: dict) -> str:
    dimensions = get_spec(data, "Габарити (ВхШхГ)")
    match = re.search(r"x([\d.,]+)\s*[смcm]*$", dimensions)
    return match.group(1) if match else ""


def build_title(data: dict, lang: str) -> str:
    color = translate_scalar(data.get("color", ""), lang)
    model = data.get("model", "").strip()
    return f"{model} {color}".strip()


def build_description(data: dict, lang: str) -> str:
    model = data.get("model", "").strip()
    brand = data.get("brand", "").strip()
    model_label = model if model.lower().startswith(brand.lower()) else f"{brand} {model}".strip()
    if lang == "uk":
        load = get_spec(data, "Завантаження")
        spin = get_spec(data, "Максимальна швидкість віджимання")
        programs = get_spec(data, "Кількість програм")
        dry = data.get("full_specifications", {}).get("Сушка") is True
        dry_load = get_spec(data, "Завантаження для сушіння")
        depth = extract_depth(data)
        inverter = data.get("full_specifications", {}).get("Інверторний двигун") is True
        steam = data.get("full_specifications", {}).get("Прання паром") is True

        extras = []
        if inverter:
            extras.append("інверторним двигуном")
        if steam:
            extras.append("пранням паром")

        base = (
            f"{'Прально-сушильна' if dry else 'Пральна'} машина {model_label} "
            f"із завантаженням {load or '—'}, віджимом до {spin or '—'}"
        )
        if dry and dry_load:
            base += f" і сушінням до {dry_load}"
        if programs:
            base += f", {programs} програмами"
        if depth:
            base += f" та глибиною {depth} см"
        base += "."
        if extras:
            base += f" Модель оснащена {', '.join(extras)}."
        base += " Підходить для щоденного прання та догляду за різними типами тканин."
        return base

    load = translate_scalar(get_spec(data, "Завантаження"), lang)
    spin = translate_scalar(get_spec(data, "Максимальна швидкість віджимання"), lang)
    programs = translate_scalar(get_spec(data, "Кількість програм"), lang)
    dry = data.get("full_specifications", {}).get("Сушка") is True
    dry_load = translate_scalar(get_spec(data, "Завантаження для сушіння"), lang)
    depth = translate_scalar(extract_depth(data), lang)
    inverter = data.get("full_specifications", {}).get("Інверторний двигун") is True
    steam = data.get("full_specifications", {}).get("Прання паром") is True

    extras = []
    if inverter:
        extras.append({"ru": "инверторным двигателем", "en": "an inverter motor"}[lang])
    if steam:
        extras.append({"ru": "обработкой паром", "en": "steam wash support"}[lang])

    if lang == "ru":
        base = (
            f"{'Стирально-сушильная' if dry else 'Стиральная'} машина {model_label} "
            f"с загрузкой {load or '—'}, отжимом до {spin or '—'}"
        )
        if dry and dry_load:
            base += f" и сушкой до {dry_load}"
        if programs:
            base += f", {programs} программами"
        if depth:
            base += f" и глубиной {depth} см"
        base += "."
        if extras:
            base += f" Модель оснащена {', '.join(extras)}."
        base += " Подходит для ежедневной стирки и ухода за разными типами тканей."
        return base

    base = (
        f"{'Washer-dryer' if dry else 'Washing machine'} {model_label} "
        f"with {load or '—'} load capacity and up to {spin or '—'} spin speed"
    )
    if dry and dry_load:
        base += f", plus drying up to {dry_load}"
    if programs:
        base += f", {programs} programs"
    if depth:
        base += f", and {depth} cm depth"
    base += "."
    if extras:
        base += f" The model features {', '.join(extras)}."
    base += " Suitable for everyday laundry and regular fabric care."
    return base


def build_meta_description(data: dict, lang: str) -> str:
    title = build_title(data, lang)
    load = get_spec(data, "Завантаження") if lang == "uk" else translate_scalar(get_spec(data, "Завантаження"), lang)
    spin = get_spec(data, "Максимальна швидкість віджимання") if lang == "uk" else translate_scalar(get_spec(data, "Максимальна швидкість віджимання"), lang)
    if lang == "uk":
        return f"{title}. Характеристики, фото, завантаження {load or '—'}, віджим до {spin or '—'}."
    if lang == "ru":
        return f"{title}. Характеристики, фото, загрузка {load or '—'}, отжим до {spin or '—'}."
    return f"{title}. Specifications, photos, {load or '—'} load capacity, up to {spin or '—'} spin speed."


def build_translated_json(uk_data: dict, lang: str) -> dict:
    full_specs = {
        key: value
        for key, value in (uk_data.get("full_specifications", {}) or {}).items()
        if key != "Дата додавання на E-Katalog"
    }
    return {
        "language": lang,
        "actual_language": lang,
        "product_url": translate_url(uk_data.get("product_url", ""), lang),
        "title": build_title(uk_data, lang),
        "description": build_description(uk_data, lang),
        "full_specifications": translate_dict(full_specs, SPEC_KEY_MAP, lang),
        "spec_sections": [
            {
                "section": SECTION_MAP.get(section.get("section", ""), {}).get(lang, section.get("section", "")),
                "specifications": translate_dict(
                    {
                        key: value
                        for key, value in (section.get("specifications", {}) or {}).items()
                        if key != "Дата додавання на E-Katalog"
                    },
                    SPEC_KEY_MAP,
                    lang,
                ),
            }
            for section in uk_data.get("spec_sections", []) or []
        ],
        "official_site_url": uk_data.get("official_site_url", ""),
        "item_added_date": translate_months(uk_data.get("item_added_date", ""), lang),
        "source_page": str(uk_data.get("source_page", "")).replace(".html", f".{lang}.html"),
    }


def update_meta(meta_data: dict) -> dict:
    meta_data["language"] = "uk"
    meta_data["language_files"] = {
        "uk": "product.uk.json",
        "ru": "product.ru.json",
        "en": "product.en.json",
    }
    versions = set(meta_data.get("language_versions_available", []))
    versions.update({"uk", "ru", "en"})
    meta_data["language_versions_available"] = sorted(versions)
    return meta_data


def update_uk_data(data: dict) -> dict:
    data["language"] = "uk"
    data["actual_language"] = "uk"
    data["title"] = build_title(data, "uk")
    data["description"] = build_description(data, "uk")
    if "full_specifications" in data and isinstance(data["full_specifications"], dict):
        data["full_specifications"].pop("Дата додавання на E-Katalog", None)
    if "spec_sections" in data and isinstance(data["spec_sections"], list):
        for section in data["spec_sections"]:
            specs = section.get("specifications")
            if isinstance(specs, dict):
                specs.pop("Дата додавання на E-Katalog", None)
    if "meta_description" in data:
        data["meta_description"] = build_meta_description(data, "uk")
    return data


def main(items_dir: Path = DEFAULT_ITEMS_DIR) -> None:
    generated = 0
    for item_dir in sorted(path for path in items_dir.iterdir() if path.is_dir()):
        meta_path = item_dir / "product.json"
        uk_path = item_dir / "product.uk.json"
        if not meta_path.exists():
            continue

        source_path = uk_path if uk_path.exists() else meta_path
        uk_data = json.loads(source_path.read_text(encoding="utf-8-sig"))
        meta_data = json.loads(meta_path.read_text(encoding="utf-8-sig"))
        uk_data = update_uk_data(uk_data)
        meta_data = update_uk_data(meta_data)

        uk_path.write_text(json.dumps(uk_data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8-sig")

        for lang in LANGS:
            out_path = item_dir / f"product.{lang}.json"
            translated = build_translated_json(uk_data, lang)
            out_path.write_text(json.dumps(translated, ensure_ascii=False, indent=4) + "\n", encoding="utf-8-sig")
            generated += 1

        meta_path.write_text(json.dumps(update_meta(meta_data), ensure_ascii=False, indent=4) + "\n", encoding="utf-8-sig")

    print(f"generated={generated}")


if __name__ == "__main__":
    main()
