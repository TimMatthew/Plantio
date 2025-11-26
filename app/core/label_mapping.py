from __future__ import annotations

# -----------------------------
# 1. Мапа рослин (label → UA)
# -----------------------------
PLANT_NAME_MAP = {
    "apple": "Яблуня",
    "cherry_sour": "Вишня (кисла)",
    "corn": "Кукурудза",
    "cucumber": "Огірок",
    "grape": "Виноград",
    "sunflower": "Соняшник",
    "wheat": "Пшениця",
    "pepper_bell": "Болгарський перець",
    "potato": "Картопля",
    "raspberry": "Малина",
    "soybean": "Соя",
    "squash": "Гарбуз",
    "strawberry": "Полуниця",
    "tomato": "Помідор",
}

# -----------------------------------
# 2. Мапа хвороб (label → UA назва)
# -----------------------------------
DISEASE_NAME_MAP = {
    "black_rot": "Чорна гниль",
    "cedar_rust": "Іржа яблуні",
    "scab": "Парша",
    "powdery_mildew": "Борошниста роса",
    "common_rust": "Іржа кукурудзи",
    "leaf_blight": "Листова плямистість",
    "bacterial_wilt": "Бактеріальне в’янення",
    "belly_rot": "Гниль плодів",
    "downy_mildew": "Пероноспороз",
    "gummy_stem_blight": "В’янення стебла",
    "pythium_rot": "Пітіумна гниль",
    "esca": "Еска винограду",
    "rhizopus_rot": "Ризопусна гниль",
    "smuts": "Сажка",
    "rust": "Іржа",
    "septoria": "Септоріоз",
    "powdery_mildew_wheat": "Борошниста роса",
    "bacterial_spot": "Бактеріальна плямистість",
    "early_blight": "Рання плямистість",
    "late_blight": "Фітофтороз",
    "leaf_mold": "Бура плямистість",
    "mosaic": "Вірус мозаїки",
    "spider_mites": "Павутинний кліщ",
    "target_spot": "Кільцева плямистість",
    "verticillium": "Вертицильоз",
    "yellow_leaf_curl_virus": "Вірус жовтого скручування листя",
    "leaf_scorch": "Плямистість листя",
    "healthy": "Здорова рослина",
}

# -------------------------------------------------------
# 3. Деякі хвороби мають різну UA назву залежно від рослини
# -------------------------------------------------------
PAIR_DISEASE_MAP = {
    ("Помідор", "late_blight"): "Фітофтороз томату",
    ("Картопля", "late_blight"): "Фітофтороз картоплі",
}

PLANT_NAME_MAP["unknown_plant"] = None
DISEASE_NAME_MAP["unknown_disease"] = "Невідома хвороба"


# -------------------------------------------------------
# 4. Основна функція нормалізації
# -------------------------------------------------------
def normalize_names(plant_label, disease_label):
    plant = PLANT_NAME_MAP.get(plant_label, plant_label)

    if disease_label in DISEASE_NAME_MAP.values():
        return plant, disease_label

    disease = DISEASE_NAME_MAP.get(disease_label, disease_label)
    return plant, disease
