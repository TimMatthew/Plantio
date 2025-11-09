import json
from pathlib import Path

RAW = [
    "0 - apple black rot",
    "1 - apple cedar rust",
    "2 - apple healthy",
    "3 - apple scab",
    "4 - cherry (sour) healthy",
    "5 - cherry (sour) powdery mildew",
    "6 - corn common rust",
    "7 - corn healthy",
    "8 - corn leaf blight",
    "9 - cucumber bacterial wilt",
    "10 - cucumber belly rot",
    "11 - cucumber downy mildew",
    "12 - cucumber fresh cucumber",
    "13 - cucumber fresh leaf",
    "14 - cucumber gummy stem blight",
    "15 - cucumber pythium fruit rot",
    "16 - grape black rot",
    "17 - grape esca (black measles)",
    "18 - grape healthy",
    "19 - grape leaf blight",
    "20 - healthy sunflower",
    "21 - healthy wheat",
    "22 - pepper bell bacterial spot",
    "23 - pepper bell healthy",
    "24 - potato early blight",
    "25 - potato healthy",
    "26 - potato late blight",
    "27 - powdery mildew wheat",
    "28 - raspberry healthy",
    "29 - rhizopus sunflower",
    "30 - rust wheat",
    "31 - septoria wheat",
    "32 - smuts wheat",
    "33 - soybean healthy",
    "34 - squash powdery mildew",
    "35 - strawberry healthy",
    "36 - strawberry leaf scorch",
    "37 - tomato bacterial spot",
    "38 - tomato healthy",
    "39 - tomato late blight",
    "40 - tomato leaf mold",
    "41 - tomato mosaic virus",
    "42 - tomato septoria leaf spot",
    "43 - tomato spider mites",
    "44 - tomato target spot",
    "45 - tomato verticulium wilt",
    "46 - tomato yellow leaf curl virus",
]

PLANTS_EN2UA = {
    "apple": "Яблуня",
    "cherry (sour)": "Вишня",
    "corn": "Кукурудза",
    "cucumber": "Огірок",
    "grape": "Виноград",
    "sunflower": "Соняшник",
    "wheat": "Пшениця",
    "pepper bell": "Перець солодкий",
    "potato": "Картопля",
    "raspberry": "Малина",
    "soybean": "Соя",
    "squash": "Кабачок",
    "strawberry": "Полуниця",
    "tomato": "Томат",
    "healthy": "здоровий",
}

DISEASES_EN2UA = {
    "black rot": "Black rot (чорна гниль)",
    "cedar rust": "Cedar rust",
    "healthy": "здоровий",
    "scab": "Парша",
    "powdery mildew": "Борошниста роса",
    "common rust": "Іржа",
    "leaf blight": "Плямистість листя",
    "bacterial wilt": "Бактеріальне в’янення",
    "belly rot": "Гниль плодів (Belly rot)",
    "downy mildew": "Несправжня борошниста роса",
    "gummy stem blight": "Gummy stem blight",
    "pythium fruit rot": "Пітіумна гниль плодів",
    "esca (black measles)": "Еска (black measles)",
    "rhizopus sunflower": "Ризопус (соняшник)",
    "rust": "Іржа",
    "septoria": "Септоріоз",
    "smuts": "Сажкові хвороби",
    "leaf scorch": "Опік листя",
    "bacterial spot": "Бактеріальна плямистість",
    "leaf mold": "Пліснява листя",
    "mosaic virus": "Вірус мозаїки",
    "spider mites": "Павутинний кліщ",
    "target spot": "Таргетна плямистість",
    "verticulium wilt": "Вертиліозне в’янення",
    "yellow leaf curl virus": "Вірус жовтої скручуваності листя",
    "early blight": "Рання плямистість (Early blight)",
    "late blight": "Фітофтороз (Late blight)",
    "fresh cucumber": "свіжий огірок",
    "fresh leaf": "свіжий лист",
}


def split_label(label: str):
    s = label.strip().lower().replace("  ", " ")
    tokens = s.split()
    if tokens[0] == "healthy":
        return (" ".join(tokens[1:]), "healthy")
    if tokens[-1] == "healthy":
        return (" ".join(tokens[:-1]), "healthy")
    if s.startswith("pepper bell "):
        return ("pepper bell", s[len("pepper bell ") :])
    if s.startswith("cherry (sour) "):
        return ("cherry (sour)", s[len("cherry (sour) ") :])
    if s.endswith(" wheat") and s.startswith("powdery mildew"):
        return ("wheat", "powdery mildew")
    if s.endswith(" wheat") and s.startswith("septoria"):
        return ("wheat", "septoria")
    if s.endswith(" wheat") and s.startswith("rust"):
        return ("wheat", "rust")
    if s.endswith(" sunflower") and s.startswith("rhizopus"):
        return ("sunflower", "rhizopus sunflower")
    first = tokens[0]
    rest = " ".join(tokens[1:])
    return (first, rest)


def main():
    out = {}
    for row in RAW:
        idx_str, label = row.split(" - ", 1)
        idx = int(idx_str.strip())
        plant_en, disease_en = split_label(label)

        plant_ua = PLANTS_EN2UA.get(plant_en, plant_en)
        disease_ua = DISEASES_EN2UA.get(disease_en, disease_en)

        out[idx] = {
            "label": label,
            "plant_en": plant_en,
            "disease_en": disease_en,
            "plant_name": plant_ua,
            "disease_name": disease_ua,
        }

    dst = Path("app/models/plantio/class_map.json")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {dst} with {len(out)} entries")


if __name__ == "__main__":
    main()
