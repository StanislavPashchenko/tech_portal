import json
import re

from django.conf import settings
from django.db.models import Count, F
from django.http import QueryDict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.text import slugify
from django.views.generic import DetailView, ListView, TemplateView

from portal.models import (
    Article,
    CatalogItem,
    ErrorCode,
    RepairApplianceType,
    RepairBrand,
    RepairModel,
)
from portal.translations import get_text


WASHING_MACHINE_FILTERS = [
    {
        "key": "brand",
        "title": "Бренд",
        "kind": "dynamic_brand",
    },
    {
        "key": "wm_type",
        "title": "Тип",
        "options": [
            {"value": "front", "label": "фронтальні"},
            {"value": "vertical", "label": "вертикальні"},
            {"value": "narrow", "label": "вузькі (до 40 см)"},
            {"value": "compact", "label": "компакт (невисокі)"},
            {"value": "semi_auto", "label": "напівавтомат (дачні)"},
        ],
    },
    {
        "key": "load",
        "title": "Завантаження",
        "options": [
            {"value": "le_5", "label": "≤ 5 кг"},
            {"value": "6", "label": "6 кг"},
            {"value": "7", "label": "7 кг"},
            {"value": "8", "label": "8 кг"},
            {"value": "9", "label": "9 кг"},
            {"value": "ge_10", "label": "≥ 10 кг"},
        ],
    },
    {
        "key": "dry_load",
        "title": "Завантаження для сушіння",
        "options": [
            {"value": "le_4", "label": "≤ 4 кг"},
            {"value": "5", "label": "5 кг"},
            {"value": "6", "label": "6 кг"},
            {"value": "ge_7", "label": "≥ 7 кг"},
        ],
    },
    {
        "key": "spin",
        "title": "Швидкість віджимання",
        "options": [
            {"value": "lt_800", "label": "< 800 об/хв"},
            {"value": "1000", "label": "1000 об/хв"},
            {"value": "1200", "label": "1200 об/хв"},
            {"value": "1400", "label": "1400 об/хв"},
            {"value": "gt_1400", "label": "> 1400 об/хв"},
        ],
    },
    {
        "key": "feature",
        "title": "Функції та можливості",
        "options": [
            {"value": "drying", "label": "сушка"},
            {"value": "no_drying", "label": "без сушіння"},
            {"value": "steam", "label": "прання паром"},
            {"value": "bubble", "label": "бульбашкове прання"},
            {"value": "spray", "label": "система прямого впорскування"},
            {"value": "auto_dosing", "label": "автоматичне дозування"},
            {"value": "intelligent", "label": "інтелектуальне прання"},
            {"value": "direct_drive", "label": "прямий привод"},
            {"value": "inverter", "label": "інверторний двигун"},
            {"value": "stainless_tank", "label": "бак з нержавіючої сталі"},
            {"value": "led", "label": "LED дисплей"},
            {"value": "tft", "label": "TFT дисплей"},
            {"value": "drum_light", "label": "підсвічування барабана"},
            {"value": "add_hatch", "label": "люк дозавантаження білизни"},
            {"value": "door_180", "label": "відкриття дверцят на 180°"},
        ],
    },
    {
        "key": "program",
        "title": "Програми",
        "options": [
            {"value": "custom", "label": "своя програма"},
            {"value": "quick", "label": "швидке прання"},
            {"value": "delicate", "label": "делікатне прання"},
            {"value": "hygiene", "label": "гігієна (дитячий одяг)"},
            {"value": "sports", "label": "спортивний одяг"},
            {"value": "dark", "label": "темний одяг"},
            {"value": "jeans", "label": "джинсовий одяг"},
            {"value": "shirts", "label": "сорочки"},
            {"value": "outerwear", "label": "верхній одяг"},
            {"value": "down", "label": "пухові речі"},
            {"value": "bedding", "label": "постільна білизна"},
            {"value": "blankets", "label": "ковдри"},
            {"value": "refresh", "label": "освіження (без прання)"},
            {"value": "night", "label": "нічна"},
            {"value": "self_clean", "label": "самоочищення"},
        ],
    },
    {
        "key": "control",
        "title": "Управління",
        "options": [
            {"value": "sensor", "label": "сенсорне"},
            {"value": "knob_buttons", "label": "поворотна ручка + кнопки"},
            {"value": "knob_sensors", "label": "поворотна ручка + сенсори"},
            {"value": "bluetooth", "label": "Bluetooth"},
            {"value": "wifi", "label": "Wi‑Fi"},
            {"value": "voice", "label": "голосовий асистент"},
        ],
    },
    {
        "key": "protection",
        "title": "Захист та контроль",
        "options": [
            {"value": "leak", "label": "захист від протікання"},
            {"value": "imbalance", "label": "контроль дисбалансу"},
            {"value": "foam", "label": "контроль піноутворення"},
            {"value": "surge", "label": "захист від перепадів напруги"},
            {"value": "child", "label": "захист від дітей"},
            {"value": "ceramic", "label": "керамічний нагрівач"},
            {"value": "nickel", "label": "нікельований ТЕН"},
        ],
    },
    {
        "key": "depth",
        "title": "Глибина",
        "options": [
            {"value": "le_35", "label": "≤ 35 см"},
            {"value": "36_40", "label": "36 – 40 см"},
            {"value": "41_45", "label": "41 – 45 см"},
            {"value": "46_50", "label": "46 – 50 см"},
            {"value": "51_55", "label": "51 – 55 см"},
            {"value": "56_60", "label": "56 – 60 см"},
            {"value": "gt_60", "label": "> 60 см"},
        ],
    },
    {
        "key": "year",
        "title": "За роком випуску",
        "options": [
            {"value": "2026", "label": "2026 р."},
            {"value": "2025", "label": "2025 р."},
            {"value": "earlier", "label": "більш ранні"},
        ],
    },
]

WASHING_MACHINE_FILTER_TITLES = {
    "brand": {"en": "Brands", "ru": "Бренды", "uk": "Бренди"},
    "wm_type": {"en": "Product type", "ru": "Тип", "uk": "Тип"},
    "load": {"en": "Capacity", "ru": "Загрузка", "uk": "Завантаження"},
    "dry_load": {"en": "Drying capacity", "ru": "Загрузка для сушки", "uk": "Завантаження для сушіння"},
    "spin": {"en": "Spin speed", "ru": "Скорость отжима", "uk": "Швидкість віджимання"},
    "feature": {"en": "Features", "ru": "Функции и возможности", "uk": "Функції та можливості"},
    "program": {"en": "Programmes", "ru": "Программы", "uk": "Програми"},
    "control": {"en": "Controls", "ru": "Управление", "uk": "Управління"},
    "protection": {"en": "Protection and control", "ru": "Защита и контроль", "uk": "Захист та контроль"},
    "depth": {"en": "Depth", "ru": "Глубина", "uk": "Глибина"},
    "year": {"en": "Release year", "ru": "Год выпуска", "uk": "За роком випуску"},
}

WASHING_MACHINE_FILTER_OPTION_LABELS = {
    "wm_type": {
        "front": {"en": "front loaded", "ru": "фронтальные", "uk": "фронтальні"},
        "vertical": {"en": "top loaded", "ru": "вертикальные", "uk": "вертикальні"},
        "narrow": {"en": "narrow (up to 40 cm)", "ru": "узкие (до 40 см)", "uk": "вузькі (до 40 см)"},
        "compact": {"en": "compact (low)", "ru": "компакт (невысокие)", "uk": "компакт (невисокі)"},
        "semi_auto": {"en": "semiautomatic", "ru": "полуавтомат", "uk": "напівавтомат (дачні)"},
    },
    "load": {
        "le_5": {"en": "≤ 5 kg", "ru": "≤ 5 кг", "uk": "≤ 5 кг"},
        "6": {"en": "6 kg", "ru": "6 кг", "uk": "6 кг"},
        "7": {"en": "7 kg", "ru": "7 кг", "uk": "7 кг"},
        "8": {"en": "8 kg", "ru": "8 кг", "uk": "8 кг"},
        "9": {"en": "9 kg", "ru": "9 кг", "uk": "9 кг"},
        "ge_10": {"en": "≥ 10 kg", "ru": "≥ 10 кг", "uk": "≥ 10 кг"},
    },
    "dry_load": {
        "le_4": {"en": "≤ 4 kg", "ru": "≤ 4 кг", "uk": "≤ 4 кг"},
        "5": {"en": "5 kg", "ru": "5 кг", "uk": "5 кг"},
        "6": {"en": "6 kg", "ru": "6 кг", "uk": "6 кг"},
        "ge_7": {"en": "≥ 7 kg", "ru": "≥ 7 кг", "uk": "≥ 7 кг"},
    },
    "spin": {
        "lt_800": {"en": "< 800 rpm", "ru": "< 800 об/мин", "uk": "< 800 об/хв"},
        "1000": {"en": "1000 rpm", "ru": "1000 об/мин", "uk": "1000 об/хв"},
        "1200": {"en": "1200 rpm", "ru": "1200 об/мин", "uk": "1200 об/хв"},
        "1400": {"en": "1400 rpm", "ru": "1400 об/мин", "uk": "1400 об/хв"},
        "gt_1400": {"en": "> 1400 rpm", "ru": "> 1400 об/мин", "uk": "> 1400 об/хв"},
    },
    "feature": {
        "drying": {"en": "dryer", "ru": "сушка", "uk": "сушка"},
        "no_drying": {"en": "no dryer", "ru": "без сушки", "uk": "без сушіння"},
        "steam": {"en": "steam wash", "ru": "стирка паром", "uk": "прання паром"},
        "bubble": {"en": "bubble wash", "ru": "пузырьковая стирка", "uk": "бульбашкове прання"},
        "spray": {"en": "direct injection system", "ru": "система прямого впрыска", "uk": "система прямого впорскування"},
        "auto_dosing": {"en": "automatic dosing", "ru": "автоматическая дозировка", "uk": "автоматичне дозування"},
        "intelligent": {"en": "smart wash", "ru": "интеллектуальная стирка", "uk": "інтелектуальне прання"},
        "direct_drive": {"en": "direct drive", "ru": "прямой привод", "uk": "прямий привід"},
        "inverter": {"en": "inverter motor", "ru": "инверторный двигатель", "uk": "інверторний двигун"},
        "stainless_tank": {"en": "stainless steel tank", "ru": "бак из нержавеющей стали", "uk": "бак з нержавіючої сталі"},
        "led": {"en": "LED display", "ru": "LED дисплей", "uk": "LED дисплей"},
        "tft": {"en": "TFT display", "ru": "TFT дисплей", "uk": "TFT дисплей"},
        "drum_light": {"en": "drum lighting", "ru": "подсветка барабана", "uk": "підсвічування барабана"},
        "add_hatch": {"en": "reloading hatch", "ru": "люк дозагрузки белья", "uk": "люк дозавантаження білизни"},
        "door_180": {"en": "180° opening door", "ru": "открытие дверцы на 180°", "uk": "відкриття дверцят на 180°"},
    },
    "program": {
        "custom": {"en": "custom programme", "ru": "своя программа", "uk": "своя програма"},
        "quick": {"en": "quick wash", "ru": "быстрая стирка", "uk": "швидке прання"},
        "delicate": {"en": "delicate", "ru": "деликатная стирка", "uk": "делікатне прання"},
        "hygiene": {"en": "hygiene (baby care)", "ru": "гигиена (детская одежда)", "uk": "гігієна (дитячий одяг)"},
        "sports": {"en": "sportswear", "ru": "спортивная одежда", "uk": "спортивний одяг"},
        "dark": {"en": "dark garment", "ru": "темная одежда", "uk": "темний одяг"},
        "jeans": {"en": "jeans", "ru": "джинсы", "uk": "джинсовий одяг"},
        "shirts": {"en": "shirts", "ru": "сорочки", "uk": "сорочки"},
        "outerwear": {"en": "outerwear", "ru": "верхняя одежда", "uk": "верхній одяг"},
        "down": {"en": "down wear", "ru": "пуховые вещи", "uk": "пухові речі"},
        "bedding": {"en": "bed linen", "ru": "постельное белье", "uk": "постільна білизна"},
        "blankets": {"en": "duvets", "ru": "одеяла", "uk": "ковдри"},
        "refresh": {"en": "refresh (no washing)", "ru": "освежение (без стирки)", "uk": "освіження (без прання)"},
        "night": {"en": "night", "ru": "ночная", "uk": "нічна"},
        "self_clean": {"en": "self clean", "ru": "самоочистка", "uk": "самоочищення"},
    },
    "control": {
        "sensor": {"en": "touch controls", "ru": "сенсорное", "uk": "сенсорне"},
        "knob_buttons": {"en": "rotary knob + buttons", "ru": "поворотная ручка + кнопки", "uk": "поворотна ручка + кнопки"},
        "knob_sensors": {"en": "rotary knob + touch controls", "ru": "поворотная ручка + сенсоры", "uk": "поворотна ручка + сенсори"},
        "bluetooth": {"en": "Bluetooth", "ru": "Bluetooth", "uk": "Bluetooth"},
        "wifi": {"en": "Wi-Fi", "ru": "Wi-Fi", "uk": "Wi-Fi"},
        "voice": {"en": "voice assistant", "ru": "голосовой ассистент", "uk": "голосовий асистент"},
    },
    "protection": {
        "leak": {"en": "leak protection", "ru": "защита от протечек", "uk": "захист від протікання"},
        "imbalance": {"en": "unbalance control", "ru": "контроль дисбаланса", "uk": "контроль дисбалансу"},
        "foam": {"en": "anti-foam control", "ru": "контроль пенообразования", "uk": "контроль піноутворення"},
        "surge": {"en": "surge protection", "ru": "защита от перепадов напряжения", "uk": "захист від перепадів напруги"},
        "child": {"en": "child lock", "ru": "защита от детей", "uk": "захист від дітей"},
        "ceramic": {"en": "ceramic heater", "ru": "керамический нагреватель", "uk": "керамічний нагрівач"},
        "nickel": {"en": "nickel-plated heater", "ru": "никелированный ТЭН", "uk": "нікельований ТЕН"},
    },
    "depth": {
        "le_35": {"en": "≤ 35 cm", "ru": "≤ 35 см", "uk": "≤ 35 см"},
        "36_40": {"en": "36 – 40 cm", "ru": "36 – 40 см", "uk": "36 – 40 см"},
        "41_45": {"en": "41 – 45 cm", "ru": "41 – 45 см", "uk": "41 – 45 см"},
        "46_50": {"en": "46 – 50 cm", "ru": "46 – 50 см", "uk": "46 – 50 см"},
        "51_55": {"en": "51 – 55 cm", "ru": "51 – 55 см", "uk": "51 – 55 см"},
        "56_60": {"en": "56 – 60 cm", "ru": "56 – 60 см", "uk": "56 – 60 см"},
        "gt_60": {"en": "> 60 cm", "ru": "> 60 см", "uk": "> 60 см"},
    },
    "year": {
        "2026": {"en": "2026", "ru": "2026 г.", "uk": "2026 р."},
        "2025": {"en": "2025", "ru": "2025 г.", "uk": "2025 р."},
        "earlier": {"en": "earlier", "ru": "более ранние", "uk": "більш ранні"},
    },
}

PROGRAM_TOKENS = {
    "custom": "своя програма",
    "quick": "швидке прання",
    "delicate": "делікатне прання",
    "hygiene": "гігієна",
    "sports": "спортивний одяг",
    "dark": "темний одяг",
    "jeans": "джинсовий одяг",
    "shirts": "сорочки",
    "outerwear": "верхній одяг",
    "down": "пухові речі",
    "bedding": "постільна білизна",
    "blankets": "ковдри",
    "refresh": "освіження",
    "night": "нічна",
    "self_clean": "самоочищення",
}

FEATURE_MATCHERS = {
    "steam": lambda specs: contains_token(specs.get("Додаткові програми", ""), "прання паром"),
    "bubble": lambda specs: contains_any_token(specs, ["бульбашкове прання"]),
    "spray": lambda specs: contains_any_token(specs, ["система прямого впорскування"]),
    "auto_dosing": lambda specs: contains_any_token(specs, ["автоматичне дозування"]),
    "intelligent": lambda specs: contains_any_token(specs, ["інтелектуальне прання"]),
    "direct_drive": lambda specs: contains_any_token(specs, ["прямий привод"]),
    "inverter": lambda specs: contains_token(specs.get("Інверторний двигун", ""), "так") or contains_any_token(specs, ["інверторний двигун"]),
    "stainless_tank": lambda specs: contains_token(specs.get("Матеріал бака", ""), "нержав"),
    "led": lambda specs: contains_token(specs.get("Дисплей", ""), "led"),
    "tft": lambda specs: contains_token(specs.get("Дисплей", ""), "tft"),
    "drum_light": lambda specs: contains_any_token(specs, ["підсвічування барабана"]),
    "add_hatch": lambda specs: contains_any_token(specs, ["люк дозавантаження білизни"]),
    "door_180": lambda specs: contains_token(specs.get("Відкриття дверцят", ""), "180"),
}

PROTECTION_MATCHERS = {
    "leak": "захист від протікання",
    "imbalance": "контроль дисбалансу",
    "foam": "контроль піноутворення",
    "surge": "захист від перепадів напруги",
    "child": "захист від дітей",
    "ceramic": "керамічний нагрівач",
    "nickel": "нікельований",
}

REFRIGERATOR_FILTERS = [
    {"key": "brand", "title": "Бренди", "kind": "dynamic_brand"},
    {
        "key": "fr_type",
        "title": "Тип",
        "options": [
            {"value": "classic", "label": "класичний"},
            {"value": "side_by_side", "label": "Side-by-side"},
            {"value": "french_door", "label": "French-door (розпашний)"},
            {"value": "display", "label": "холодильна вітрина"},
        ],
    },
    {
        "key": "chambers",
        "title": "Кількість камер",
        "options": [
            {"value": "1", "label": "однокамерні"},
            {"value": "2", "label": "двокамерні"},
            {"value": "3", "label": "трикамерні"},
            {"value": "4_plus", "label": "багатокамерні"},
        ],
    },
    {
        "key": "freezer",
        "title": "Морозилка",
        "options": [
            {"value": "top", "label": "зверху"},
            {"value": "bottom", "label": "знизу"},
            {"value": "bottom_drawer", "label": "знизу (висувна)"},
            {"value": "side", "label": "збоку"},
            {"value": "none", "label": "відсутня"},
        ],
    },
    {
        "key": "feature",
        "title": "Функції та можливості",
        "options": [
            {"value": "full_no_frost", "label": "повністю No Frost"},
            {"value": "freezer_no_frost", "label": "морозилка з No Frost"},
            {"value": "no_no_frost", "label": "без No Frost (крапельні)"},
            {"value": "inverter", "label": "інверторний компресор"},
            {"value": "quick_freeze", "label": "швидка заморозка"},
            {"value": "fast_cool", "label": "швидке охолодження"},
            {"value": "dynamic_cooling", "label": "динамічне охолодження"},
            {"value": "performant_freezer", "label": "продуктивна морозилка"},
            {"value": "freezer_temp", "label": "t морозилки -24 °C і нижче"},
            {"value": "holiday", "label": "режим відпустки"},
            {"value": "deodorizer", "label": "дезодоратор"},
            {"value": "two_circuits", "label": "2 контури охолодження"},
            {"value": "two_compressors", "label": "2 компресори"},
        ],
    },
    {
        "key": "compartment",
        "title": "Відсіки",
        "options": [
            {"value": "fresh_zone", "label": "зона свіжості (нульова камера)"},
            {"value": "humidity_zone", "label": "зона вологості"},
            {"value": "multizone", "label": "мультизона"},
            {"value": "wine", "label": "камера для вина"},
            {"value": "bottle_rack", "label": "полиця для пляшок"},
            {"value": "foldable_shelf", "label": "складана полиця"},
            {"value": "minibar", "label": "швидкий доступ (міні-бар)"},
            {"value": "water", "label": "диспенсер для води"},
            {"value": "ice", "label": "генератор льоду"},
            {"value": "big_drawer", "label": "великий ящик морозилки"},
            {"value": "slim_shelf", "label": "слім-полиця морозилки"},
        ],
    },
    {
        "key": "extra",
        "title": "Додатково",
        "options": [
            {"value": "retro", "label": "ретро дизайн"},
            {"value": "door_alarm", "label": "індикатор закриття дверцят"},
            {"value": "reversible", "label": "перевішування дверей"},
            {"value": "hidden_handles", "label": "приховані ручки дверей"},
            {"value": "regular_handle", "label": "звичайна ручка"},
            {"value": "handle_light", "label": "підсвічування ручок"},
            {"value": "telescope_fridge", "label": "«телескопи» (холодильник)"},
            {"value": "telescope_freezer", "label": "«телескопи» (морозильник)"},
            {"value": "led_light", "label": "LED освітлення"},
            {"value": "led_display", "label": "LED дисплей"},
            {"value": "tft_display", "label": "TFT дисплей"},
            {"value": "child_lock", "label": "захист від дітей"},
            {"value": "surge", "label": "захист від перепадів напруги"},
            {"value": "internet", "label": "управління через Internet"},
            {"value": "glass_panel", "label": "скляне оздоблення дверцят"},
            {"value": "custom_panel", "label": "змінна панель (декоративна)"},
        ],
    },
    {"key": "height", "title": "Висота", "options": [{"value": "le_85", "label": "≤ 85 см"}, {"value": "86_100", "label": "86 – 100 см"}, {"value": "101_125", "label": "101 – 125 см"}, {"value": "126_150", "label": "126 – 150 см"}, {"value": "151_170", "label": "151 – 170 см"}, {"value": "171_180", "label": "171 – 180 см"}, {"value": "181_190", "label": "181 – 190 см"}, {"value": "191_200", "label": "191 – 200 см"}, {"value": "gt_200", "label": "> 2 м"}]},
    {"key": "width", "title": "Ширина", "options": [{"value": "45", "label": "45 см"}, {"value": "50", "label": "50 см"}, {"value": "55", "label": "55 см"}, {"value": "60", "label": "60 см"}, {"value": "65", "label": "65 см"}, {"value": "70", "label": "70 см"}, {"value": "75", "label": "75 см"}, {"value": "80", "label": "80 см"}, {"value": "85", "label": "85 см"}, {"value": "90", "label": "90 см"}, {"value": "120", "label": "120 см"}]},
    {"key": "energy", "title": "Клас енергоспоживання", "options": [{"value": "a_new", "label": "A (new)"}, {"value": "b_new", "label": "B (new)"}, {"value": "c_new", "label": "C (new)"}, {"value": "d_new", "label": "D (new)"}, {"value": "e_new", "label": "E (new)"}, {"value": "f_new", "label": "F (new)"}, {"value": "a3", "label": "A+++"}, {"value": "a2", "label": "A++"}, {"value": "a1", "label": "A+"}]},
    {"key": "year", "title": "За роком випуску", "options": [{"value": "2026", "label": "2026 р."}, {"value": "2025", "label": "2025 р."}, {"value": "earlier", "label": "більш ранні"}]},
    {"key": "climate", "title": "Кліматичний клас", "options": [{"value": "SN", "label": "SN"}, {"value": "N", "label": "N"}, {"value": "ST", "label": "ST"}, {"value": "T", "label": "T"}]},
    {"key": "control", "title": "Управління", "options": [{"value": "sensor_inner", "label": "сенсорне внутрішнє"}, {"value": "sensor_outer", "label": "сенсорне зовнішнє"}, {"value": "rotary", "label": "поворотні перемикачі"}, {"value": "buttons_inner", "label": "кнопкове внутрішнє"}]},
    {"key": "fridge_volume", "title": "Об'єм холодильної камери", "options": [{"value": "le_100", "label": "≤ 100 л"}, {"value": "101_200", "label": "101 – 200 л"}, {"value": "201_250", "label": "201 – 250 л"}, {"value": "251_300", "label": "251 – 300 л"}, {"value": "gt_300", "label": "> 300 л"}]},
    {"key": "shelves", "title": "Полиць холодильної камери", "options": [{"value": "2", "label": "2"}, {"value": "3", "label": "3"}, {"value": "4", "label": "4"}, {"value": "5", "label": "5"}, {"value": "ge_6", "label": "≥ 6"}]},
    {"key": "freezer_volume", "title": "Об'єм морозилки", "options": [{"value": "le_50", "label": "≤ 50 л"}, {"value": "51_100", "label": "51 – 100 л"}, {"value": "101_150", "label": "101 – 150 л"}, {"value": "gt_150", "label": "> 150 л"}]},
    {"key": "drawers", "title": "Ящиків морозильної камери", "options": [{"value": "1_2", "label": "1 – 2"}, {"value": "3", "label": "3"}, {"value": "4", "label": "4"}, {"value": "ge_5", "label": "≥ 5"}]},
    {"key": "autonomy", "title": "Час збереження холоду", "options": [{"value": "le_10", "label": "≤ 10 год"}, {"value": "11_20", "label": "11 – 20 год"}, {"value": "21_30", "label": "21 – 30 год"}, {"value": "gt_30", "label": "> 30 год"}]},
    {"key": "noise", "title": "Рівень шуму", "options": [{"value": "le_35", "label": "≤ 35 дБ"}, {"value": "36_39", "label": "36 – 39 дБ"}, {"value": "40_42", "label": "40 – 42 дБ"}, {"value": "gt_42", "label": "> 42 дБ"}]},
    {"key": "depth", "title": "Глибина", "options": [{"value": "le_55", "label": "≤ 55 см"}, {"value": "56_60", "label": "56 – 60 см"}, {"value": "61_65", "label": "61 – 65 см"}, {"value": "66_70", "label": "66 – 70 см"}, {"value": "gt_70", "label": "> 70 см"}]},
    {"key": "country", "title": "Країна виробництва", "kind": "dynamic_country"},
]

REFRIGERATOR_FILTER_TITLES = {
    "brand": {"en": "Brands", "ru": "Бренды", "uk": "Бренди"},
    "fr_type": {"en": "Product type", "ru": "Тип", "uk": "Тип"},
    "chambers": {"en": "Number of chambers", "ru": "Количество камер", "uk": "Кількість камер"},
    "freezer": {"en": "Freezer", "ru": "Морозилка", "uk": "Морозилка"},
    "feature": {"en": "Features", "ru": "Функции и возможности", "uk": "Функції та можливості"},
    "compartment": {"en": "Compartments", "ru": "Отсеки", "uk": "Відсіки"},
    "extra": {"en": "More features", "ru": "Дополнительно", "uk": "Додатково"},
    "height": {"en": "Height", "ru": "Высота", "uk": "Висота"},
    "width": {"en": "Width", "ru": "Ширина", "uk": "Ширина"},
    "energy": {"en": "Energy class", "ru": "Класс энергопотребления", "uk": "Клас енергоспоживання"},
    "year": {"en": "Release year", "ru": "Год выпуска", "uk": "За роком випуску"},
    "climate": {"en": "Climate class", "ru": "Климатический класс", "uk": "Кліматичний клас"},
    "control": {"en": "Controls", "ru": "Управление", "uk": "Управління"},
    "fridge_volume": {"en": "Refrigerator capacity", "ru": "Объем холодильной камеры", "uk": "Об'єм холодильної камери"},
    "shelves": {"en": "Refrigerator shelves", "ru": "Полок холодильной камеры", "uk": "Полиць холодильної камери"},
    "freezer_volume": {"en": "Freezer capacity", "ru": "Объем морозилки", "uk": "Об'єм морозилки"},
    "drawers": {"en": "Freezer drawers", "ru": "Ящиков морозильной камеры", "uk": "Ящиків морозильної камери"},
    "autonomy": {"en": "Autonomy time", "ru": "Время сохранения холода", "uk": "Час збереження холоду"},
    "noise": {"en": "Noise level", "ru": "Уровень шума", "uk": "Рівень шуму"},
    "depth": {"en": "Depth", "ru": "Глубина", "uk": "Глибина"},
    "country": {"en": "Country of Origin", "ru": "Страна производства", "uk": "Країна виробництва"},
}

REFRIGERATOR_FILTER_OPTION_LABELS = {
    "fr_type": {
        "classic": {"en": "classic", "ru": "классический", "uk": "класичний"},
        "side_by_side": {"en": "Side-by-side", "ru": "Side-by-side", "uk": "Side-by-side"},
        "french_door": {"en": "French door", "ru": "French-door (распашный)", "uk": "French-door (розпашний)"},
        "display": {"en": "display refrigerator", "ru": "холодильная витрина", "uk": "холодильна вітрина"},
    },
    "chambers": {
        "1": {"en": "single chamber", "ru": "однокамерные", "uk": "однокамерні"},
        "2": {"en": "two chambers", "ru": "двухкамерные", "uk": "двокамерні"},
        "3": {"en": "three chambers", "ru": "трехкамерные", "uk": "трикамерні"},
        "4_plus": {"en": "multi-chamber", "ru": "многокамерные", "uk": "багатокамерні"},
    },
    "freezer": {
        "top": {"en": "top", "ru": "сверху", "uk": "зверху"},
        "bottom": {"en": "bottom", "ru": "снизу", "uk": "знизу"},
        "bottom_drawer": {"en": "bottom (retractable)", "ru": "снизу (выдвижная)", "uk": "знизу (висувна)"},
        "side": {"en": "side", "ru": "сбоку", "uk": "збоку"},
        "none": {"en": "no freezer", "ru": "отсутствует", "uk": "відсутня"},
    },
    "feature": {
        "full_no_frost": {"en": "full No Frost", "ru": "полностью No Frost", "uk": "повністю No Frost"},
        "freezer_no_frost": {"en": "No Frost freezer", "ru": "морозилка с No Frost", "uk": "морозилка з No Frost"},
        "no_no_frost": {"en": "no No Frost (self-defrosting)", "ru": "без No Frost (капельные)", "uk": "без No Frost (крапельні)"},
        "inverter": {"en": "inverter compressor", "ru": "инверторный компрессор", "uk": "інверторний компресор"},
        "quick_freeze": {"en": "fast freeze", "ru": "быстрая заморозка", "uk": "швидка заморозка"},
        "fast_cool": {"en": "fast cool", "ru": "быстрое охлаждение", "uk": "швидке охолодження"},
        "dynamic_cooling": {"en": "dynamic air cooling", "ru": "динамическое охлаждение", "uk": "динамічне охолодження"},
        "performant_freezer": {"en": "performant freezer", "ru": "производительная морозилка", "uk": "продуктивна морозилка"},
        "freezer_temp": {"en": "freezer T= -24 °C and below", "ru": "t морозилки -24 °C и ниже", "uk": "t морозилки -24 °C і нижче"},
        "holiday": {"en": "holiday mode", "ru": "режим отпуска", "uk": "режим відпустки"},
        "deodorizer": {"en": "deodorizer", "ru": "дезодоратор", "uk": "дезодоратор"},
        "two_circuits": {"en": "2 cooling circuits", "ru": "2 контура охлаждения", "uk": "2 контури охолодження"},
        "two_compressors": {"en": "2 compressors", "ru": "2 компрессора", "uk": "2 компресори"},
    },
    "compartment": {
        "fresh_zone": {"en": "fresh zone (zero chamber)", "ru": "зона свежести (нулевая камера)", "uk": "зона свіжості (нульова камера)"},
        "humidity_zone": {"en": "humidity zone", "ru": "зона влажности", "uk": "зона вологості"},
        "multizone": {"en": "multizone", "ru": "мультизона", "uk": "мультизона"},
        "wine": {"en": "wine chamber", "ru": "камера для вина", "uk": "камера для вина"},
        "bottle_rack": {"en": "bottle rack", "ru": "полка для бутылок", "uk": "полиця для пляшок"},
        "foldable_shelf": {"en": "foldable shelf", "ru": "складная полка", "uk": "складана полиця"},
        "minibar": {"en": "quick access (minibar)", "ru": "быстрый доступ (мини-бар)", "uk": "швидкий доступ (міні-бар)"},
        "water": {"en": "water dispenser", "ru": "диспенсер для воды", "uk": "диспенсер для води"},
        "ice": {"en": "ice maker", "ru": "генератор льда", "uk": "генератор льоду"},
        "big_drawer": {"en": "big freezer drawer", "ru": "большой ящик морозилки", "uk": "великий ящик морозилки"},
        "slim_shelf": {"en": "freezer slim shelf", "ru": "слим-полка морозилки", "uk": "слім-полиця морозилки"},
    },
    "extra": {
        "retro": {"en": "retro design", "ru": "ретро дизайн", "uk": "ретро дизайн"},
        "door_alarm": {"en": "door alarm", "ru": "индикатор закрытия дверцы", "uk": "індикатор закриття дверцят"},
        "reversible": {"en": "reversible door", "ru": "перевешивание дверей", "uk": "перевішування дверей"},
        "hidden_handles": {"en": "hidden door handles", "ru": "скрытые ручки дверей", "uk": "приховані ручки дверей"},
        "regular_handle": {"en": "regular handle", "ru": "обычная ручка", "uk": "звичайна ручка"},
        "handle_light": {"en": "handle illumination", "ru": "подсветка ручек", "uk": "підсвічування ручок"},
        "telescope_fridge": {"en": "telescopic rails (refrigerator)", "ru": "«телескопы» (холодильник)", "uk": "«телескопи» (холодильник)"},
        "telescope_freezer": {"en": "telescopic rails (freezer)", "ru": "«телескопы» (морозильник)", "uk": "«телескопи» (морозильник)"},
        "led_light": {"en": "LED light", "ru": "LED освещение", "uk": "LED освітлення"},
        "led_display": {"en": "LED display", "ru": "LED дисплей", "uk": "LED дисплей"},
        "tft_display": {"en": "TFT display", "ru": "TFT дисплей", "uk": "TFT дисплей"},
        "child_lock": {"en": "child lock", "ru": "защита от детей", "uk": "захист від дітей"},
        "surge": {"en": "surge protection", "ru": "защита от перепадов напряжения", "uk": "захист від перепадів напруги"},
        "internet": {"en": "control via Internet", "ru": "управление через Internet", "uk": "управління через Internet"},
        "glass_panel": {"en": "glass door panel", "ru": "стеклянная отделка дверцы", "uk": "скляне оздоблення дверцят"},
        "custom_panel": {"en": "customizable panel", "ru": "сменная панель (декоративная)", "uk": "змінна панель (декоративна)"},
    },
}


def split_content_blocks(text):
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    return blocks or [text]


def get_language_code():
    return (translation.get_language() or settings.LANGUAGE_CODE)[:2]


def build_breadcrumbs(crumbs):
    breadcrumbs = [
        {"label": get_text("home", get_language_code()), "url": reverse("portal:home")}
    ]
    breadcrumbs.extend(crumbs)
    return breadcrumbs


def contains_token(value, token):
    return token.lower() in (value or "").lower()


def contains_any_token(specs, tokens):
    haystack = " ".join(f"{key} {value}" for key, value in (specs or {}).items()).lower()
    return any(token.lower() in haystack for token in tokens)


def parse_first_number(value):
    match = re.search(r"(\d+(?:[.,]\d+)?)", value or "")
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def parse_dimensions(value):
    matches = re.findall(r"(\d+(?:[.,]\d+)?)", value or "")
    if len(matches) < 3:
        return None
    height, width, depth = [float(match.replace(",", ".")) for match in matches[:3]]
    return {"height": height, "width": width, "depth": depth}


def parse_year(value):
    match = re.search(r"(20\d{2})", value or "")
    return int(match.group(1)) if match else None


def is_washing_machine_context(appliance_type):
    return appliance_type and appliance_type.slug == "washing-machines"


def get_filter_translation(mapping, key, language, fallback):
    values = mapping.get(key, {})
    return values.get(language) or values.get("uk") or values.get("en") or fallback


def build_washing_machine_filter_groups(appliance_type, language=None):
    language = (language or get_language_code())[:2]
    groups = []
    brand_options = []
    if appliance_type:
        brands = (
            RepairBrand.objects.filter(appliance_type=appliance_type)
            .annotate(product_count=Count("repair_models__catalog_item", distinct=True))
            .filter(product_count__gt=0)
            .order_by("name")
        )
        for brand in brands:
            brand_options.append({"value": brand.slug, "label": brand.display_name})

    for group in WASHING_MACHINE_FILTERS:
        if group.get("kind") == "dynamic_brand":
            groups.append(
                {
                    **group,
                    "title": get_filter_translation(WASHING_MACHINE_FILTER_TITLES, group["key"], language, group["title"]),
                    "options": brand_options,
                }
            )
        else:
            groups.append(
                {
                    **group,
                    "title": get_filter_translation(WASHING_MACHINE_FILTER_TITLES, group["key"], language, group["title"]),
                    "options": [
                        {
                            **option,
                            "label": get_filter_translation(
                                WASHING_MACHINE_FILTER_OPTION_LABELS.get(group["key"], {}),
                                option["value"],
                                language,
                                option["label"],
                            ),
                        }
                        for option in group["options"]
                    ],
                }
            )
    return groups


def is_refrigerator_context(appliance_type):
    return appliance_type and appliance_type.slug == "refrigerators"


def get_refrigerator_filter_groups(appliance_type, language=None):
    language = (language or get_language_code())[:2]
    groups = []
    brand_options = []
    country_options = {}
    if appliance_type:
        brands = (
            RepairBrand.objects.filter(appliance_type=appliance_type)
            .annotate(product_count=Count("repair_models__catalog_item", distinct=True))
            .filter(product_count__gt=0)
            .order_by("name")
        )
        for brand in brands:
            brand_options.append({"value": brand.slug, "label": brand.display_name})

        item_specs = CatalogItem.objects.filter(
            repair_model__repair_brand__appliance_type=appliance_type
        ).values_list("short_specs", "short_specs_ru", "short_specs_en")
        for specs_uk, specs_ru, specs_en in item_specs:
            country = extract_country_from_spec_sets(specs_uk, specs_ru, specs_en, language)
            if country:
                country_options[slugify(country)] = {"value": slugify(country), "label": country}

    for group in REFRIGERATOR_FILTERS:
        if group.get("kind") == "dynamic_brand":
            groups.append(
                {
                    **group,
                    "title": get_filter_translation(
                        REFRIGERATOR_FILTER_TITLES,
                        group["key"],
                        language,
                        group["title"],
                    ),
                    "options": brand_options,
                }
            )
        elif group.get("kind") == "dynamic_country":
            groups.append(
                {
                    **group,
                    "title": get_filter_translation(
                        REFRIGERATOR_FILTER_TITLES,
                        group["key"],
                        language,
                        group["title"],
                    ),
                    "options": sorted(country_options.values(), key=lambda option: option["label"]),
                }
            )
        else:
            groups.append(
                {
                    **group,
                    "title": get_filter_translation(
                        REFRIGERATOR_FILTER_TITLES,
                        group["key"],
                        language,
                        group["title"],
                    ),
                    "options": [
                        {
                            **option,
                            "label": get_filter_translation(
                                REFRIGERATOR_FILTER_OPTION_LABELS.get(group["key"], {}),
                                option["value"],
                                language,
                                option["label"],
                            ),
                        }
                        for option in group["options"]
                    ],
                }
            )
    return groups


def filter_washing_machine_items(items, request_get):
    selected = {key: request_get.getlist(key) for key in ("brand", "wm_type", "load", "dry_load", "spin", "feature", "program", "control", "protection", "depth", "year")}
    filtered_items = []
    for item in items:
        specs = item.short_specs or {}
        brand_slug = item.repair_model.repair_brand.slug
        if selected["brand"] and brand_slug not in selected["brand"]:
            continue
        if selected["wm_type"] and not matches_wm_type(specs, selected["wm_type"]):
            continue
        if selected["load"] and not matches_load_bucket(specs.get("Завантаження", ""), selected["load"]):
            continue
        if selected["dry_load"] and not matches_dry_load_bucket(specs.get("Завантаження для сушіння", ""), selected["dry_load"]):
            continue
        if selected["spin"] and not matches_spin_bucket(specs.get("Максимальна швидкість віджимання", ""), selected["spin"]):
            continue
        if selected["feature"] and not matches_features(specs, selected["feature"]):
            continue
        if selected["program"] and not matches_programs(specs.get("Додаткові програми", ""), selected["program"]):
            continue
        if selected["control"] and not matches_controls(specs, selected["control"]):
            continue
        if selected["protection"] and not matches_protections(specs.get("Функції безпеки", ""), selected["protection"]):
            continue
        if selected["depth"] and not matches_depth_bucket(specs.get("Габарити (ВхШхГ)", ""), selected["depth"]):
            continue
        if selected["year"] and not matches_year_bucket(specs.get("Дата додавання на E-Katalog", ""), selected["year"]):
            continue
        filtered_items.append(item)
    return filtered_items, selected


def has_active_filters(selected_filters):
    return any(selected_filters.get(key) for key in selected_filters)


def matches_wm_type(specs, selected_values):
    loading_type = (specs.get("Тип завантаження", "") or "").lower()
    dimensions = parse_dimensions(specs.get("Габарити (ВхШхГ)", ""))
    heater = (specs.get("Матеріал ТЕНу", "") or "").lower()
    for value in selected_values:
        if value == "front" and "фронталь" in loading_type:
            return True
        if value == "vertical" and "вертикаль" in loading_type:
            return True
        if value == "narrow" and dimensions and dimensions["depth"] <= 40:
            return True
        if value == "compact" and dimensions and dimensions["height"] <= 70:
            return True
        if value == "semi_auto" and "тен відсутній" in heater:
            return True
    return False


def matches_load_bucket(value, selected_values):
    amount = parse_first_number(value)
    if amount is None:
        return False
    for bucket in selected_values:
        if bucket == "le_5" and amount <= 5:
            return True
        if bucket == "6" and 5.5 <= amount < 6.5:
            return True
        if bucket == "7" and 6.5 <= amount < 7.5:
            return True
        if bucket == "8" and 7.5 <= amount < 8.5:
            return True
        if bucket == "9" and 8.5 <= amount < 9.5:
            return True
        if bucket == "ge_10" and amount >= 9.5:
            return True
    return False


def matches_dry_load_bucket(value, selected_values):
    amount = parse_first_number(value)
    if amount is None:
        return False
    for bucket in selected_values:
        if bucket == "le_4" and amount <= 4:
            return True
        if bucket == "5" and 4.5 <= amount < 5.5:
            return True
        if bucket == "6" and 5.5 <= amount < 6.5:
            return True
        if bucket == "ge_7" and amount >= 6.5:
            return True
    return False


def matches_spin_bucket(value, selected_values):
    amount = parse_first_number(value)
    if amount is None:
        return False
    for bucket in selected_values:
        if bucket == "lt_800" and amount < 800:
            return True
        if bucket == "1000" and 950 <= amount < 1100:
            return True
        if bucket == "1200" and 1150 <= amount < 1300:
            return True
        if bucket == "1400" and 1350 <= amount <= 1400:
            return True
        if bucket == "gt_1400" and amount > 1400:
            return True
    return False


def matches_features(specs, selected_values):
    dry_load = parse_first_number(specs.get("Завантаження для сушіння", ""))
    for value in selected_values:
        if value == "drying" and dry_load:
            return True
        if value == "no_drying" and dry_load is None:
            return True
        matcher = FEATURE_MATCHERS.get(value)
        if matcher and matcher(specs):
            return True
    return False


def matches_programs(value, selected_values):
    text = (value or "").lower()
    for selected_value in selected_values:
        token = PROGRAM_TOKENS.get(selected_value)
        if token and token.lower() in text:
            return True
    return False


def matches_controls(specs, selected_values):
    control_value = (specs.get("Управління", "") or "").lower()
    smart_value = (specs.get("Керування зі смартфона", "") or "").lower()
    all_text = " ".join((control_value, smart_value))
    for value in selected_values:
        if value == "sensor" and "сенсор" in control_value:
            return True
        if value == "knob_buttons" and "ручка + кнопки" in control_value:
            return True
        if value == "knob_sensors" and "ручка + сенсори" in control_value:
            return True
        if value == "bluetooth" and "bluetooth" in all_text:
            return True
        if value == "wifi" and "wi-fi" in all_text:
            return True
        if value == "voice" and contains_any_token(specs, ["голосовий асистент"]):
            return True
    return False


def matches_protections(value, selected_values):
    text = (value or "").lower()
    for selected_value in selected_values:
        token = PROTECTION_MATCHERS.get(selected_value)
        if token and token.lower() in text:
            return True
    return False


def matches_depth_bucket(value, selected_values):
    dimensions = parse_dimensions(value)
    if not dimensions:
        return False
    depth = dimensions["depth"]
    for bucket in selected_values:
        if bucket == "le_35" and depth <= 35:
            return True
        if bucket == "36_40" and 36 <= depth <= 40:
            return True
        if bucket == "41_45" and 41 <= depth <= 45:
            return True
        if bucket == "46_50" and 46 <= depth <= 50:
            return True
        if bucket == "51_55" and 51 <= depth <= 55:
            return True
        if bucket == "56_60" and 56 <= depth <= 60:
            return True
        if bucket == "gt_60" and depth > 60:
            return True
    return False


def matches_year_bucket(value, selected_values):
    year = parse_year(value)
    if year is None:
        return False
    for bucket in selected_values:
        if bucket == "2026" and year == 2026:
            return True
        if bucket == "2025" and year == 2025:
            return True
        if bucket == "earlier" and year < 2025:
            return True
    return False


def get_refrigerator_filter_text(item):
    if hasattr(item, "_refrigerator_filter_text"):
        return item._refrigerator_filter_text
    parts = []
    for specs in (item.short_specs or {}, item.short_specs_ru or {}, item.short_specs_en or {}):
        parts.extend(f"{key} {value}" for key, value in specs.items())
    parts.extend(
        value
        for value in (
            item.product_description,
            item.product_description_ru,
            item.product_description_en,
        )
        if value
    )
    item._refrigerator_filter_text = " ".join(parts).lower()
    return item._refrigerator_filter_text


def matches_refrigerator_type(specs, selected_values):
    type_value = (specs.get("Тип", "") or "").lower()
    for value in selected_values:
        if value == "side_by_side" and "side-by-side" in type_value:
            return True
        if value == "french_door" and "french-door" in type_value:
            return True
        if value == "display" and "вітрина" in type_value:
            return True
        if value == "classic" and not any(token in type_value for token in ("side-by-side", "french-door", "вітрина")):
            return True
    return False


def matches_refrigerator_chambers(specs, selected_values):
    amount = parse_first_number(specs.get("Кількість камер", ""))
    if amount is None:
        return False
    for bucket in selected_values:
        if bucket == "1" and amount == 1:
            return True
        if bucket == "2" and amount == 2:
            return True
        if bucket == "3" and amount == 3:
            return True
        if bucket == "4_plus" and amount >= 4:
            return True
    return False


def matches_refrigerator_freezer(specs, selected_values):
    freezer_value = (specs.get("Морозильна камера", "") or "").lower()
    mapping = {
        "top": "зверху",
        "bottom": "знизу",
        "bottom_drawer": "знизу (висувна)",
        "side": "збоку",
        "none": "немає",
    }
    return any(mapping.get(value) == freezer_value for value in selected_values)


def matches_refrigerator_features(item, specs, selected_values):
    text = get_refrigerator_filter_text(item)
    no_frost = (specs.get("No Frost", "") or "").lower()
    circuits = parse_first_number(specs.get("Контурів охолодження", ""))
    compressors = parse_first_number(specs.get("Компресорів", ""))
    freeze_power = parse_first_number(specs.get("Потужність заморожування", ""))
    freeze_temp = parse_first_number(specs.get("Температура морозилки", ""))

    for value in selected_values:
        if value == "full_no_frost" and "морозильна / холодильна" in no_frost:
            return True
        if value == "freezer_no_frost" and "морозильна камера" in no_frost:
            return True
        if value == "no_no_frost" and not no_frost:
            return True
        if value == "inverter" and "інверторн" in text:
            return True
        if value == "quick_freeze" and "швидке заморожування" in text:
            return True
        if value == "fast_cool" and "швидке охолодження" in text:
            return True
        if value == "dynamic_cooling" and "динамічне охолодження" in text:
            return True
        if value == "performant_freezer" and freeze_power is not None and freeze_power >= 8:
            return True
        if value == "freezer_temp" and freeze_temp is not None and freeze_temp <= -24:
            return True
        if value == "holiday" and "режим відпустки" in text:
            return True
        if value == "deodorizer" and "дезодоратор" in text:
            return True
        if value == "two_circuits" and circuits is not None and circuits >= 2:
            return True
        if value == "two_compressors" and compressors is not None and compressors >= 2:
            return True
    return False


def matches_refrigerator_compartments(item, specs, selected_values):
    text = get_refrigerator_filter_text(item)
    for value in selected_values:
        if value == "fresh_zone" and ("зона свіжості" in text or "нульова камера" in text):
            return True
        if value == "humidity_zone" and "зона вологості" in text:
            return True
        if value == "multizone" and "мультизона" in text:
            return True
        if value == "wine" and ("камера для вина" in text or "об'єм камери для вина" in text or "wine" in text):
            return True
        if value == "bottle_rack" and "полиця для пляшок" in text:
            return True
        if value == "foldable_shelf" and "складна полиця" in text:
            return True
        if value == "minibar" and ("міні-бар" in text or "швидкий доступ" in text):
            return True
        if value == "water" and "диспенсер холодної води" in text:
            return True
        if value == "ice" and "льодогенератор" in text:
            return True
        if value == "big_drawer" and "великий ящик морозилки" in text:
            return True
        if value == "slim_shelf" and ("слім-полиця морозилки" in text or "висувна полиця швидкого доступу" in text):
            return True
    return False


def matches_refrigerator_extras(item, specs, selected_values):
    text = get_refrigerator_filter_text(item)
    for value in selected_values:
        if value == "retro" and "ретро" in text:
            return True
        if value == "door_alarm" and "індикатор закриття дверцят" in text:
            return True
        if value == "reversible" and "перевішування дверей" in text:
            return True
        if value == "hidden_handles" and "приховані ручки дверей" in text:
            return True
        if value == "regular_handle" and ("звичайна ручка" in text or "виступаючі ручки" in text):
            return True
        if value == "handle_light" and "підсвічування ручок" in text:
            return True
        if value == "telescope_fridge" and ("телескопіч" in text and "холодиль" in text):
            return True
        if value == "telescope_freezer" and ("телескопіч" in text and "мороз" in text):
            return True
        if value == "led_light" and "led освітлення" in text:
            return True
        if value == "led_display" and "led дисплей" in text:
            return True
        if value == "tft_display" and "tft дисплей" in text:
            return True
        if value == "child_lock" and "захист від дітей" in text:
            return True
        if value == "surge" and "захист від перепадів напруги" in text:
            return True
        if value == "internet" and ("керування зі смартфона" in text or "через інтернет" in text):
            return True
        if value == "glass_panel" and "скляне оздоблення дверцят" in text:
            return True
        if value == "custom_panel" and "змінна панель" in text:
            return True
    return False


def matches_range_bucket(value, selected_values, ranges):
    amount = parse_first_number(value)
    if amount is None:
        return False
    for bucket, lower, upper in ranges:
        if bucket not in selected_values:
            continue
        if lower is None and amount <= upper:
            return True
        if upper is None and amount > lower:
            return True
        if lower is not None and upper is not None and lower <= amount <= upper:
            return True
    return False


def matches_width_bucket(value, selected_values):
    dimensions = parse_dimensions(value)
    if not dimensions:
        return False
    width = dimensions["width"]
    for bucket in selected_values:
        target = float(bucket)
        if abs(width - target) <= 2.5:
            return True
    return False


def matches_energy_bucket(specs, selected_values):
    new_class = (specs.get("Клас енергоспоживання (new)", "") or "").upper()
    old_class = (specs.get("Клас енергоспоживання", "") or "").upper()
    mapping = {
        "a_new": "A",
        "b_new": "B",
        "c_new": "C",
        "d_new": "D",
        "e_new": "E",
        "f_new": "F",
        "a3": "A+++",
        "a2": "A++",
        "a1": "A+",
    }
    for bucket in selected_values:
        token = mapping[bucket]
        if bucket.endswith("_new") and token in new_class:
            return True
        if not bucket.endswith("_new") and token in old_class:
            return True
    return False


def matches_climate_bucket(value, selected_values):
    text = (value or "").upper()
    return any(bucket in text for bucket in selected_values)


def matches_refrigerator_controls(value, selected_values):
    text = (value or "").lower()
    for bucket in selected_values:
        if bucket == "sensor_inner" and "сенсорне внутрішнє" in text:
            return True
        if bucket == "sensor_outer" and "сенсорне зовнішнє" in text:
            return True
        if bucket == "rotary" and "поворотні перемикачі" in text:
            return True
        if bucket == "buttons_inner" and "кнопкове внутрішнє" in text:
            return True
    return False


def matches_country_filter(item, selected_values, language):
    country = extract_country_from_spec_sets(item.short_specs, item.short_specs_ru, item.short_specs_en, language)
    if not country:
        return False
    return slugify(country) in selected_values


def extract_country_from_spec_sets(specs_uk, specs_ru, specs_en, language):
    ordered_specs = {
        "uk": (specs_uk, specs_ru, specs_en),
        "ru": (specs_ru, specs_uk, specs_en),
        "en": (specs_en, specs_uk, specs_ru),
    }.get(language, (specs_uk, specs_ru, specs_en))

    for specs in ordered_specs:
        if not isinstance(specs, dict):
            continue
        country = (
            specs.get("Країна виробництва")
            or specs.get("Страна производства")
            or specs.get("Country of origin")
        )
        if isinstance(country, str):
            country = country.strip()
            if country:
                return country
    return ""


def has_selected_values(request_get, keys):
    return any(request_get.getlist(key) for key in keys)


def filter_refrigerator_items(items, request_get, language=None):
    selected_keys = [
        "brand",
        "fr_type",
        "chambers",
        "freezer",
        "feature",
        "compartment",
        "extra",
        "height",
        "width",
        "energy",
        "year",
        "climate",
        "control",
        "fridge_volume",
        "shelves",
        "freezer_volume",
        "drawers",
        "autonomy",
        "noise",
        "depth",
        "country",
    ]
    selected = {key: request_get.getlist(key) for key in selected_keys}
    filtered_items = []
    language = (language or get_language_code())[:2]

    for item in items:
        specs = item.short_specs or {}
        if selected["brand"] and item.repair_model.repair_brand.slug not in selected["brand"]:
            continue
        if selected["fr_type"] and not matches_refrigerator_type(specs, selected["fr_type"]):
            continue
        if selected["chambers"] and not matches_refrigerator_chambers(specs, selected["chambers"]):
            continue
        if selected["freezer"] and not matches_refrigerator_freezer(specs, selected["freezer"]):
            continue
        if selected["feature"] and not matches_refrigerator_features(item, specs, selected["feature"]):
            continue
        if selected["compartment"] and not matches_refrigerator_compartments(item, specs, selected["compartment"]):
            continue
        if selected["extra"] and not matches_refrigerator_extras(item, specs, selected["extra"]):
            continue
        if selected["height"] and not matches_range_bucket(specs.get("Габарити (ВхШхГ)", ""), selected["height"], [("le_85", None, 85), ("86_100", 86, 100), ("101_125", 101, 125), ("126_150", 126, 150), ("151_170", 151, 170), ("171_180", 171, 180), ("181_190", 181, 190), ("191_200", 191, 200), ("gt_200", 200, None)]):
            continue
        if selected["width"] and not matches_width_bucket(specs.get("Габарити (ВхШхГ)", ""), selected["width"]):
            continue
        if selected["energy"] and not matches_energy_bucket(specs, selected["energy"]):
            continue
        if selected["year"] and not matches_year_bucket(specs.get("Дата додавання на E-Katalog", ""), selected["year"]):
            continue
        if selected["climate"] and not matches_climate_bucket(specs.get("Кліматичний клас", ""), selected["climate"]):
            continue
        if selected["control"] and not matches_refrigerator_controls(specs.get("Управління", ""), selected["control"]):
            continue
        if selected["fridge_volume"] and not matches_range_bucket(specs.get("Об'єм холодильної камери", ""), selected["fridge_volume"], [("le_100", None, 100), ("101_200", 101, 200), ("201_250", 201, 250), ("251_300", 251, 300), ("gt_300", 300, None)]):
            continue
        if selected["shelves"] and not matches_range_bucket(specs.get("Полиць", ""), selected["shelves"], [("2", 1.5, 2.5), ("3", 2.5, 3.5), ("4", 3.5, 4.5), ("5", 4.5, 5.5), ("ge_6", 5.5, None)]):
            continue
        if selected["freezer_volume"] and not matches_range_bucket(specs.get("Об'єм морозильної камери", ""), selected["freezer_volume"], [("le_50", None, 50), ("51_100", 51, 100), ("101_150", 101, 150), ("gt_150", 150, None)]):
            continue
        if selected["drawers"] and not matches_range_bucket(specs.get("Відділень морозильної камери", ""), selected["drawers"], [("1_2", 1, 2), ("3", 2.5, 3.5), ("4", 3.5, 4.5), ("ge_5", 4.5, None)]):
            continue
        if selected["autonomy"] and not matches_range_bucket(specs.get("Час збереження холоду", ""), selected["autonomy"], [("le_10", None, 10), ("11_20", 11, 20), ("21_30", 21, 30), ("gt_30", 30, None)]):
            continue
        if selected["noise"] and not matches_range_bucket(specs.get("Рівень шуму", ""), selected["noise"], [("le_35", None, 35), ("36_39", 36, 39), ("40_42", 40, 42), ("gt_42", 42, None)]):
            continue
        if selected["depth"] and not matches_range_bucket(specs.get("Габарити (ВхШхГ)", ""), selected["depth"], [("le_55", None, 55), ("56_60", 56, 60), ("61_65", 61, 65), ("66_70", 66, 70), ("gt_70", 70, None)]):
            continue
        if selected["country"] and not matches_country_filter(item, selected["country"], language):
            continue
        filtered_items.append(item)
    return filtered_items, selected


class SeoContextMixin:
    def seo_context(self, **kwargs):
        return {
            "page_title": kwargs.get("page_title", settings.SITE_NAME),
            "meta_description": kwargs.get(
                "meta_description", settings.DEFAULT_META_DESCRIPTION
            ),
            "canonical_url": kwargs.get(
                "canonical_url", self.request.build_absolute_uri(self.request.path)
            ),
            "og_type": kwargs.get("og_type", "website"),
            "og_image": kwargs.get("og_image"),
            "meta_robots": kwargs.get("meta_robots", "index,follow"),
            "breadcrumbs": kwargs.get("breadcrumbs", []),
        }

    def breadcrumb_schema(self, breadcrumbs):
        item_list = []
        for index, crumb in enumerate(breadcrumbs, start=1):
            item_list.append(
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": crumb["label"],
                    "item": self.request.build_absolute_uri(crumb["url"]),
                }
            )
        return json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": item_list,
            },
            ensure_ascii=False,
        )


class LocalizedTemplateMixin:
    def get_template_names(self):
        template_names = super().get_template_names()
        language = get_language_code()
        localized_templates = []
        for template_name in template_names:
            if template_name.startswith("portal/"):
                localized_templates.append(
                    f"portal/{language}/{template_name.removeprefix('portal/')}"
                )
        return localized_templates + template_names


class PaginationContextMixin:
    pagination_window = 2

    def get_pagination_context(self, page_obj):
        if not page_obj or page_obj.paginator.num_pages <= 1:
            return {}

        current = page_obj.number
        total = page_obj.paginator.num_pages
        start = max(1, current - self.pagination_window)
        end = min(total, current + self.pagination_window)
        page_numbers = list(range(start, end + 1))

        query = self.request.GET.copy()
        if not isinstance(query, QueryDict):
            query = QueryDict("", mutable=True)
        query.pop("page", None)
        querystring = query.urlencode()
        if querystring:
            querystring = f"&{querystring}"

        return {
            "page_numbers": page_numbers,
            "pagination_querystring": querystring,
            "show_first_page": 1 not in page_numbers,
            "show_last_page": total not in page_numbers,
        }


class HomeView(LocalizedTemplateMixin, SeoContextMixin, TemplateView):
    template_name = "portal/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        article_queryset = (
            Article.objects.published()
            .select_related("category", "brand")
            .localized(language)
        )
        latest_errors = ErrorCode.objects.select_related(
            "repair_model",
            "repair_model__repair_brand",
            "repair_model__repair_brand__appliance_type",
        ).localized(language)[:6]
        latest_products = CatalogItem.objects.select_related(
            "repair_model",
            "repair_model__repair_brand",
            "repair_model__repair_brand__appliance_type",
        )[:8]
        product_appliance_types = (
            RepairApplianceType.objects.annotate(
                product_count=Count("repair_brands__repair_models__catalog_item", distinct=True)
            )
            .filter(product_count__gt=0)
            .order_by("name")
        )
        breadcrumbs = [{"label": get_text("home", language), "url": reverse("portal:home")}]
        context.update(
            {
                "hero_articles": article_queryset[:3],
                "latest_articles": article_queryset[:8],
                "latest_errors": latest_errors,
                "latest_products": latest_products,
                "product_appliance_types": product_appliance_types,
                "page_heading": get_text("site_name", language),
                "intro_text": get_text("home_intro", language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{settings.SITE_NAME} | {get_text('site_tagline', language)}",
                meta_description=settings.DEFAULT_META_DESCRIPTION,
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ArticleListView(LocalizedTemplateMixin, PaginationContextMixin, SeoContextMixin, ListView):
    template_name = "portal/article_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        language = get_language_code()
        return (
            Article.objects.published()
            .select_related("category", "brand")
            .localized(language)
            .order_by("-featured", "-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        breadcrumbs = build_breadcrumbs(
            [{"label": get_text("articles", language), "url": reverse("portal:article_list")}]
        )
        context.update(self.get_pagination_context(context.get("page_obj")))
        context.update(
            {
                "page_heading": get_text("articles", language),
                "page_intro": get_text("latest_articles", language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{get_text('articles', language)} | {settings.SITE_NAME}",
                meta_description=get_text("latest_articles", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ErrorApplianceTypeListView(LocalizedTemplateMixin, SeoContextMixin, ListView):
    template_name = "portal/error_type_list.html"
    context_object_name = "appliance_types"
    queryset = RepairApplianceType.objects.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        breadcrumbs = build_breadcrumbs(
            [{"label": get_text("latest_error_codes", language), "url": reverse("portal:error_list")}]
        )
        context.update(
            {
                "page_heading": get_text("error_type_heading", language),
                "page_intro": get_text("error_type_intro", language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{get_text('latest_error_codes', language)} | {settings.SITE_NAME}",
                meta_description=get_text("error_type_intro", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ErrorBrandListView(LocalizedTemplateMixin, SeoContextMixin, ListView):
    template_name = "portal/error_brand_list.html"
    context_object_name = "repair_brands"

    def get_queryset(self):
        return RepairBrand.objects.select_related("appliance_type").filter(
            appliance_type__slug=self.kwargs["type_slug"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        appliance_type = get_object_or_404(RepairApplianceType, slug=self.kwargs["type_slug"])
        breadcrumbs = build_breadcrumbs(
            [
                {"label": get_text("latest_error_codes", language), "url": reverse("portal:error_list")},
                {"label": appliance_type.display_name, "url": reverse("portal:error_type", kwargs={"type_slug": appliance_type.slug})},
            ]
        )
        context.update(
            {
                "appliance_type": appliance_type,
                "page_heading": appliance_type.display_name,
                "page_intro": get_text("error_brand_intro", language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{appliance_type.display_name} | {settings.SITE_NAME}",
                meta_description=get_text("error_brand_intro", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ErrorModelListView(LocalizedTemplateMixin, SeoContextMixin, ListView):
    template_name = "portal/error_model_list.html"
    context_object_name = "repair_models"

    def get_queryset(self):
        return RepairModel.objects.select_related(
            "repair_brand",
            "repair_brand__appliance_type",
            "catalog_item",
        ).filter(
            repair_brand__appliance_type__slug=self.kwargs["type_slug"],
            repair_brand__slug=self.kwargs["brand_slug"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        repair_brand = get_object_or_404(
            RepairBrand.objects.select_related("appliance_type"),
            appliance_type__slug=self.kwargs["type_slug"],
            slug=self.kwargs["brand_slug"],
        )
        breadcrumbs = build_breadcrumbs(
            [
                {"label": get_text("latest_error_codes", language), "url": reverse("portal:error_list")},
                {
                    "label": repair_brand.appliance_type.display_name,
                    "url": reverse("portal:error_type", kwargs={"type_slug": repair_brand.appliance_type.slug}),
                },
                {
                    "label": repair_brand.display_name,
                    "url": reverse(
                        "portal:error_brand",
                        kwargs={
                            "type_slug": repair_brand.appliance_type.slug,
                            "brand_slug": repair_brand.slug,
                        },
                    ),
                },
            ]
        )
        context.update(
            {
                "appliance_type": repair_brand.appliance_type,
                "repair_brand": repair_brand,
                "page_heading": repair_brand.display_name,
                "page_intro": get_text("error_model_intro", language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{repair_brand.display_name} | {settings.SITE_NAME}",
                meta_description=get_text("error_model_intro", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ErrorCodeListView(LocalizedTemplateMixin, PaginationContextMixin, SeoContextMixin, ListView):
    template_name = "portal/error_list.html"
    context_object_name = "error_codes"
    paginate_by = 12

    def get_queryset(self):
        language = get_language_code()
        return (
            ErrorCode.objects.select_related(
                "repair_model",
                "repair_model__repair_brand",
                "repair_model__repair_brand__appliance_type",
            )
            .localized(language)
            .filter(
                repair_model__repair_brand__appliance_type__slug=self.kwargs["type_slug"],
                repair_model__repair_brand__slug=self.kwargs["brand_slug"],
                repair_model__slug=self.kwargs["model_slug"],
            )
            .order_by("code", "title")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        repair_model = get_object_or_404(
            RepairModel.objects.select_related("repair_brand", "repair_brand__appliance_type"),
            repair_brand__appliance_type__slug=self.kwargs["type_slug"],
            repair_brand__slug=self.kwargs["brand_slug"],
            slug=self.kwargs["model_slug"],
        )
        breadcrumbs = build_breadcrumbs(
            [
                {"label": get_text("latest_error_codes", language), "url": reverse("portal:error_list")},
                {
                    "label": repair_model.repair_brand.appliance_type.display_name,
                    "url": reverse("portal:error_type", kwargs={"type_slug": repair_model.repair_brand.appliance_type.slug}),
                },
                {
                    "label": repair_model.repair_brand.display_name,
                    "url": reverse(
                        "portal:error_brand",
                        kwargs={
                            "type_slug": repair_model.repair_brand.appliance_type.slug,
                            "brand_slug": repair_model.repair_brand.slug,
                        },
                    ),
                },
                {
                    "label": repair_model.display_name,
                    "url": reverse(
                        "portal:error_model",
                        kwargs={
                            "type_slug": repair_model.repair_brand.appliance_type.slug,
                            "brand_slug": repair_model.repair_brand.slug,
                            "model_slug": repair_model.slug,
                        },
                    ),
                },
            ]
        )
        context.update(self.get_pagination_context(context.get("page_obj")))
        context.update(
            {
                "repair_model": repair_model,
                "page_heading": repair_model.display_name,
                "page_intro": get_text("error_code_list_intro", language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{repair_model.display_name} | {settings.SITE_NAME}",
                meta_description=get_text("error_code_list_intro", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ProductListView(LocalizedTemplateMixin, PaginationContextMixin, SeoContextMixin, ListView):
    template_name = "portal/product_list.html"
    context_object_name = "products"
    paginate_by = 18

    def get_queryset(self):
        return CatalogItem.objects.select_related(
            "repair_model",
            "repair_model__repair_brand",
            "repair_model__repair_brand__appliance_type",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        product_appliance_types = (
            RepairApplianceType.objects.annotate(
                product_count=Count("repair_brands__repair_models__catalog_item", distinct=True)
            )
            .filter(product_count__gt=0)
            .order_by("name")
        )
        breadcrumbs = build_breadcrumbs(
            [{"label": get_text("products", language), "url": reverse("portal:product_list")}]
        )
        context.update(self.get_pagination_context(context.get("page_obj")))
        context.update(
            {
                "page_heading": get_text("products", language),
                "page_intro": get_text("product_catalog_intro", language),
                "product_appliance_types": product_appliance_types,
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{get_text('products', language)} | {settings.SITE_NAME}",
                meta_description=get_text("product_catalog_intro", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ProductApplianceTypeListView(ProductListView):
    WASHING_MACHINE_FILTER_KEYS = ("brand", "wm_type", "load", "dry_load", "spin", "feature", "program", "control", "protection", "depth", "year")
    REFRIGERATOR_FILTER_KEYS = (
        "brand", "fr_type", "chambers", "freezer", "feature", "compartment", "extra",
        "height", "width", "energy", "year", "climate", "control", "fridge_volume",
        "shelves", "freezer_volume", "drawers", "autonomy", "noise", "depth", "country",
    )

    def get_appliance_type(self):
        if not hasattr(self, "_appliance_type"):
            self._appliance_type = get_object_or_404(RepairApplianceType, slug=self.kwargs["type_slug"])
        return self._appliance_type

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(repair_model__repair_brand__appliance_type__slug=self.kwargs["type_slug"])
        )
        appliance_type = self.get_appliance_type()
        if is_washing_machine_context(appliance_type):
            if not has_selected_values(self.request.GET, self.WASHING_MACHINE_FILTER_KEYS):
                self.selected_product_filters = {key: [] for key in self.WASHING_MACHINE_FILTER_KEYS}
                return queryset
            filtered_items, selected_filters = filter_washing_machine_items(list(queryset), self.request.GET)
            self.selected_product_filters = selected_filters
            return filtered_items
        if is_refrigerator_context(appliance_type):
            if not has_selected_values(self.request.GET, self.REFRIGERATOR_FILTER_KEYS):
                self.selected_product_filters = {key: [] for key in self.REFRIGERATOR_FILTER_KEYS}
                return queryset
            filtered_items, selected_filters = filter_refrigerator_items(list(queryset), self.request.GET, get_language_code())
            self.selected_product_filters = selected_filters
            return filtered_items
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        appliance_type = self.get_appliance_type()
        product_brands = (
            RepairBrand.objects.filter(appliance_type=appliance_type)
            .annotate(product_count=Count("repair_models__catalog_item", distinct=True))
            .filter(product_count__gt=0)
            .order_by("name")
        )
        breadcrumbs = build_breadcrumbs(
            [
                {"label": get_text("products", language), "url": reverse("portal:product_list")},
                {
                    "label": appliance_type.display_name,
                    "url": reverse("portal:product_type", kwargs={"type_slug": appliance_type.slug}),
                },
            ]
        )
        context.update(
            {
                "appliance_type": appliance_type,
                "page_heading": appliance_type.display_name,
                "page_intro": appliance_type.display_description or get_text("product_catalog_intro", language),
                "product_brands": product_brands,
                "show_product_filters": is_washing_machine_context(appliance_type) or is_refrigerator_context(appliance_type),
                "product_filter_groups": build_washing_machine_filter_groups(appliance_type, language) if is_washing_machine_context(appliance_type) else get_refrigerator_filter_groups(appliance_type, language),
                "selected_product_filters": getattr(self, "selected_product_filters", {}),
                "product_filters_active": has_active_filters(getattr(self, "selected_product_filters", {})),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{appliance_type.get_seo_title(language)} | {settings.SITE_NAME}",
                meta_description=appliance_type.get_meta_description(language) or get_text("product_catalog_intro", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ProductBrandListView(ProductListView):
    def get_repair_brand(self):
        if not hasattr(self, "_repair_brand"):
            self._repair_brand = get_object_or_404(
                RepairBrand.objects.select_related("appliance_type"),
                appliance_type__slug=self.kwargs["type_slug"],
                slug=self.kwargs["brand_slug"],
            )
        return self._repair_brand

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(
                repair_model__repair_brand__appliance_type__slug=self.kwargs["type_slug"],
                repair_model__repair_brand__slug=self.kwargs["brand_slug"],
            )
        )
        repair_brand = self.get_repair_brand()
        if is_washing_machine_context(repair_brand.appliance_type):
            if not has_selected_values(self.request.GET, ProductApplianceTypeListView.WASHING_MACHINE_FILTER_KEYS):
                self.selected_product_filters = {key: [] for key in ProductApplianceTypeListView.WASHING_MACHINE_FILTER_KEYS}
                return queryset
            filtered_items, selected_filters = filter_washing_machine_items(list(queryset), self.request.GET)
            self.selected_product_filters = selected_filters
            return filtered_items
        if is_refrigerator_context(repair_brand.appliance_type):
            if not has_selected_values(self.request.GET, ProductApplianceTypeListView.REFRIGERATOR_FILTER_KEYS):
                self.selected_product_filters = {key: [] for key in ProductApplianceTypeListView.REFRIGERATOR_FILTER_KEYS}
                return queryset
            filtered_items, selected_filters = filter_refrigerator_items(list(queryset), self.request.GET, get_language_code())
            self.selected_product_filters = selected_filters
            return filtered_items
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        repair_brand = self.get_repair_brand()
        breadcrumbs = build_breadcrumbs(
            [
                {"label": get_text("products", language), "url": reverse("portal:product_list")},
                {
                    "label": repair_brand.appliance_type.display_name,
                    "url": reverse("portal:product_type", kwargs={"type_slug": repair_brand.appliance_type.slug}),
                },
                {
                    "label": repair_brand.display_name,
                    "url": reverse(
                        "portal:product_brand",
                        kwargs={
                            "type_slug": repair_brand.appliance_type.slug,
                            "brand_slug": repair_brand.slug,
                        },
                    ),
                },
            ]
        )
        context.update(
            {
                "appliance_type": repair_brand.appliance_type,
                "repair_brand": repair_brand,
                "page_heading": repair_brand.display_name,
                "page_intro": repair_brand.display_description or get_text("product_catalog_intro", language),
                "show_product_filters": is_washing_machine_context(repair_brand.appliance_type) or is_refrigerator_context(repair_brand.appliance_type),
                "product_filter_groups": build_washing_machine_filter_groups(repair_brand.appliance_type, language) if is_washing_machine_context(repair_brand.appliance_type) else get_refrigerator_filter_groups(repair_brand.appliance_type, language),
                "selected_product_filters": getattr(self, "selected_product_filters", {}),
                "product_filters_active": has_active_filters(getattr(self, "selected_product_filters", {})),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{repair_brand.get_seo_title(language)} | {settings.SITE_NAME}",
                meta_description=repair_brand.get_meta_description(language) or get_text("product_catalog_intro", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ArticleDetailView(LocalizedTemplateMixin, SeoContextMixin, DetailView):
    template_name = "portal/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        language = get_language_code()
        return (
            Article.objects.published()
            .select_related("category", "brand", "device")
            .localized(language)
        )

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        article = get_object_or_404(queryset, slug=self.kwargs["slug"])
        Article.objects.filter(pk=article.pk).update(views=F("views") + 1)
        article.refresh_from_db()
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = context["article"]
        language = get_language_code()
        related_articles = (
            Article.objects.published()
            .select_related("category", "brand")
            .exclude(pk=article.pk)
            .order_by("-featured", "-created_at")
            .localized(language)[:4]
        )
        breadcrumbs = build_breadcrumbs(
            [{"label": article.display_title, "url": article.get_absolute_url()}]
        )
        content_blocks = split_content_blocks(article.display_content)
        article_schema = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": article.display_title,
                "description": article.get_meta_description(language),
                "datePublished": article.created_at.isoformat(),
                "dateModified": article.updated_at.isoformat(),
                "author": {"@type": "Organization", "name": settings.SITE_NAME},
                "publisher": {"@type": "Organization", "name": settings.SITE_NAME},
                "mainEntityOfPage": self.request.build_absolute_uri(article.get_absolute_url()),
                "image": [article.image] if article.image else [],
                "articleSection": settings.SITE_NAME,
            },
            ensure_ascii=False,
        )
        context.update(
            {
                "content_blocks": content_blocks,
                "midpoint_index": max(1, len(content_blocks) // 2),
                "related_articles": related_articles,
                "article_schema": article_schema,
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{article.get_seo_title(language)} | {settings.SITE_NAME}",
                meta_description=article.get_meta_description(language),
                og_type="article",
                og_image=article.image,
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ProductDetailView(LocalizedTemplateMixin, SeoContextMixin, DetailView):
    template_name = "portal/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return CatalogItem.objects.select_related(
            "repair_model",
            "repair_model__repair_brand",
            "repair_model__repair_brand__appliance_type",
        ).prefetch_related("images", "faults", "repair_model__error_codes")

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        product = get_object_or_404(
            queryset,
            repair_model__repair_brand__appliance_type__slug=self.kwargs["type_slug"],
            repair_model__repair_brand__slug=self.kwargs["brand_slug"],
            repair_model__slug=self.kwargs["slug"],
        )
        CatalogItem.objects.filter(pk=product.pk).update(views=F("views") + 1)
        product.refresh_from_db()
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context["product"]
        language = get_language_code()
        related_products = (
            CatalogItem.objects.select_related(
                "repair_model",
                "repair_model__repair_brand",
                "repair_model__repair_brand__appliance_type",
            )
            .filter(repair_model__repair_brand=product.repair_model.repair_brand)
            .exclude(pk=product.pk)[:6]
        )
        breadcrumbs = build_breadcrumbs(
            [
                {"label": get_text("products", language), "url": reverse("portal:product_list")},
                {
                    "label": product.display_appliance_type,
                    "url": reverse(
                        "portal:product_type",
                        kwargs={"type_slug": product.repair_model.repair_brand.appliance_type.slug},
                    ),
                },
                {
                    "label": product.display_brand_name,
                    "url": reverse(
                        "portal:product_brand",
                        kwargs={
                            "type_slug": product.repair_model.repair_brand.appliance_type.slug,
                            "brand_slug": product.repair_model.repair_brand.slug,
                        },
                    ),
                },
                {"label": product.display_name, "url": product.get_absolute_url()},
            ]
        )
        context.update(
            {
                "error_codes": product.repair_model.error_codes.order_by("code", "title"),
                "related_products": related_products,
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{product.get_seo_title(language)} | {settings.SITE_NAME}",
                meta_description=product.get_meta_description(language) or product.product_description,
                og_type="article",
                og_image=product.primary_image,
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ErrorCodeDetailView(LocalizedTemplateMixin, SeoContextMixin, DetailView):
    template_name = "portal/error_detail.html"
    context_object_name = "error_code"

    def get_queryset(self):
        language = get_language_code()
        return (
            ErrorCode.objects.select_related(
                "repair_model",
                "repair_model__repair_brand",
                "repair_model__repair_brand__appliance_type",
            )
            .localized(language)
            .filter(
                repair_model__repair_brand__appliance_type__slug=self.kwargs["type_slug"],
                repair_model__repair_brand__slug=self.kwargs["brand_slug"],
                repair_model__slug=self.kwargs["model_slug"],
            )
            .order_by("code", "title")
        )

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        error_code = get_object_or_404(queryset, slug=self.kwargs["slug"])
        ErrorCode.objects.filter(pk=error_code.pk).update(views=F("views") + 1)
        error_code.refresh_from_db()
        return error_code

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_code = context["error_code"]
        language = get_language_code()
        related_error_codes = (
            ErrorCode.objects.select_related(
                "repair_model",
                "repair_model__repair_brand",
                "repair_model__repair_brand__appliance_type",
            )
            .localized(language)
            .filter(repair_model=error_code.repair_model)
            .exclude(pk=error_code.pk)
            .order_by("code", "title")[:6]
        )
        breadcrumbs = build_breadcrumbs(
            [
                {"label": get_text("latest_error_codes", language), "url": reverse("portal:error_list")},
                {
                    "label": error_code.display_appliance_type,
                    "url": reverse(
                        "portal:error_type",
                        kwargs={"type_slug": error_code.repair_model.repair_brand.appliance_type.slug},
                    ),
                },
                {
                    "label": error_code.display_brand_name,
                    "url": reverse(
                        "portal:error_brand",
                        kwargs={
                            "type_slug": error_code.repair_model.repair_brand.appliance_type.slug,
                            "brand_slug": error_code.repair_model.repair_brand.slug,
                        },
                    ),
                },
                {
                    "label": error_code.display_model_name,
                    "url": reverse(
                        "portal:error_model",
                        kwargs={
                            "type_slug": error_code.repair_model.repair_brand.appliance_type.slug,
                            "brand_slug": error_code.repair_model.repair_brand.slug,
                            "model_slug": error_code.repair_model.slug,
                        },
                    ),
                },
                {"label": error_code.code, "url": error_code.get_absolute_url()},
            ]
        )
        error_schema = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": error_code.display_title,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": error_code.display_solutions,
                        },
                    }
                ],
            },
            ensure_ascii=False,
        )
        context.update(
            {
                "related_error_codes": related_error_codes,
                "error_schema": error_schema,
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{error_code.get_seo_title(language)} | {settings.SITE_NAME}",
                meta_description=error_code.get_meta_description(language),
                og_type="article",
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class SearchView(LocalizedTemplateMixin, SeoContextMixin, TemplateView):
    template_name = "portal/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        query = self.request.GET.get("q", "").strip()
        article_results = Article.objects.none()
        error_results = ErrorCode.objects.none()
        product_results = CatalogItem.objects.none()
        if query:
            article_results = (
                Article.objects.published()
                .select_related("category", "brand")
                .localized(language)
                .search(query)
            )
            error_results = ErrorCode.objects.localized(language).search(query)
            product_results = CatalogItem.objects.select_related(
                "repair_model",
                "repair_model__repair_brand",
                "repair_model__repair_brand__appliance_type",
            ).search(query)
        breadcrumbs = build_breadcrumbs(
            [{"label": get_text("search", language), "url": reverse("portal:search")}]
        )
        context.update(
            {
                "query": query,
                "article_results": article_results[:12],
                "error_results": error_results[:12],
                "product_results": product_results[:12],
                "results_total": article_results.count() + error_results.count() + product_results.count() if query else 0,
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{get_text('search', language)} | {settings.SITE_NAME}",
                meta_description=get_text("search_description", language),
                meta_robots="noindex,follow",
                breadcrumbs=breadcrumbs,
            )
        )
        return context


def robots_txt(request):
    return render(
        request,
        "robots.txt",
        {
            "sitemap_url": request.build_absolute_uri(reverse("sitemap")),
            "generated_at": timezone.now(),
        },
        content_type="text/plain",
    )
