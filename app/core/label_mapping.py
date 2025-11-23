from __future__ import annotations

PLANT_NAME_MAP: dict[str, str] = {
    # яблуня
    "apple": "Яблуня",
    "Яблуня": "Яблуня",
    # вишня
    "cherry (sour)": "Вишня (кисла)",
    "Вишня (кисла)": "Вишня (кисла)",
    # кукурудза
    "corn": "Кукурудза",
    "Кукурудза": "Кукурудза",
    # огірок
    "cucumber": "Огірок",
    "Огірок": "Огірок",
    # виноград
    "grape": "Виноград",
    "Виноград": "Виноград",
    # болгарський перець
    "pepper bell": "Болгарський перець",
    "Болгарський перець": "Болгарський перець",
    # картопля
    "potato": "Картопля",
    "Картопля": "Картопля",
    # пшениця
    "wheat": "Пшениця",
    "Пшениця": "Пшениця",
    # соняшник
    "sunflower": "Соняшник",
    "Соняшник": "Соняшник",
    # малина
    "raspberry": "Малина",
    "Малина": "Малина",
    # соя
    "soybean": "Соя",
    "Соя": "Соя",
    # гарбуз
    "squash": "Гарбуз",
    "Гарбуз": "Гарбуз",
    # полуниця
    "strawberry": "Полуниця",
    "Полуниця": "Полуниця",
    # помідор
    "tomato": "Помідор",
    "Помідор": "Помідор",
    # спеціальні "штучні" класи для пшениці
    "Powdery": "Пшениця",
    "Rust": "Пшениця",
    "Septoria": "Пшениця",
    "Smuts": "Пшениця",
    "powdery": "Пшениця",
    "rust": "Пшениця",
    "septoria": "Пшениця",
    "smuts": "Пшениця",
    # Rhizopus
    "Rhizopus": "Соняшник",
    "rhizopus": "Соняшник",
}


DISEASE_NAME_MAP: dict[str, str] = {
    # Apple
    "Black rot (чорна гниль)": "Чорна гниль",
    "Cedar apple rust (іржа яблуні від ялівцю)": "Ржавчина яблуні",
    "Scab (парша)": "Парша яблуні",
    # Sour cherry
    "Powdery mildew (борошниста роса)": "Борошниста роса",
    # Corn
    "Common rust": "Ржавчина кукурудзи",
    "Leaf blight": "Бура північна плямистість / гельмінтоспоріоз",
    # Cucumber
    "Cucumber Bacterial Wilt / Cucumber Belly Rot": "Cucumber Bacterial Wilt / Cucumber Belly Rot",
    "Cucumber Downy Mildew": "Пероноспороз огірків або несправжня борошниста роса",
    "Cucumber Fresh Cucumber / Fresh Leaf": "Свіжий огірок",
    "Cucumber Gummy Stem Blight": "В'янення огірка",
    "Cucumber Pythium Fruit Rot": "Пітіумна гниль огірків",
    # Grape
    "Grape Black Rot": "Чорна плямистість",
    "Grape Esca (Black Measles)": "Еска винограду",
    "Grape Leaf Blight": "Листова плямистість винограду",
    # Potato
    "Early Blight": "Рання суха плямистість картоплі",
    # Wheat
    "Mildew Wheat": "Борошниста роса пшениці",
    # Squash
    "Powdery Mildew": "Борошниста роса гарбузових",
    # Strawberry
    "Leaf Scorch": "Бура плямистість полуниці",
    # Sunflower / Rhizopus
    "Sunflower": "Ризопусна гниль соняшника",
    # Tomato
    "Tomato Mosaic Virus": "Вірус мозаїки томату",
    "Septoria Leaf Spot": "Септоріоз листя томату або біла плямистість томату",
    "Spider Mites": "Ураження томату павутинним кліщем",
    "Target Spot": "Кільцева плямистість томату або альтернаріоз томату",
    "Verticillium Wilt": "Вертицильозне в'янення томату або вертицильоз томату",
    "Tomato Yellow Leaf Curl Virus": "Вірус жовтого скручування листя томату",
    "Leaf Mold": "Бура плямистість листя томату або кладоспоріоз томату",
}


PAIR_DISEASE_NAME_MAP: dict[tuple[str, str], str] = {
    # Tomato vs Potato Late Blight
    ("Помідор", "Late Blight"): "Фітофтороз томату",
    ("Картопля", "Late Blight"): "Фітофтороз картоплі",
    # Wheat: Rust / Septoria / Smuts
    ("Rust", "Wheat"): "Іржа",
    ("Septoria", "Wheat"): "Септоріоз",
    ("Smuts", "Wheat"): "Сажка",
    # Bacterial Spot
    ("Помідор", "Bacterial Spot"): "Бактеріальна плямистість томату",
    ("Болгарський перець", "Bacterial Spot"): "Бактеріальна плямистість",
    # Sunflower
    ("Соняшник", "Rhizopus"): "Ризопусна гниль соняшника",
}


def normalize_names(
    plant_name: str | None,
    disease_name: str | None,
) -> tuple[str | None, str | None, bool]:
    """
    Повертає (plant_name_norm, disease_name_norm, mapped_any)

    mapped_any = True, якщо хоч щось замепилось.
    """
    mapped = False

    plant_norm = plant_name
    disease_norm = disease_name

    if plant_name:
        key = plant_name.strip()
        if key in PLANT_NAME_MAP:
            plant_norm = PLANT_NAME_MAP[key]
            mapped = True

    if plant_name and disease_name:
        pair_key = (plant_name.strip(), disease_name.strip())
        if pair_key in PAIR_DISEASE_NAME_MAP:
            disease_norm = PAIR_DISEASE_NAME_MAP[pair_key]
            mapped = True

    if disease_name and disease_norm == disease_name:
        key = disease_name.strip()
        if key in DISEASE_NAME_MAP:
            disease_norm = DISEASE_NAME_MAP[key]
            mapped = True

    return plant_norm, disease_norm, mapped
