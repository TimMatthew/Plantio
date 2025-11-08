import asyncio

from app.db.init_db import init_db
from app.models.disease import Disease
from app.models.plant import Plant

plants = [
    {
        "id": "pl_sunflower",
        "name": {"uk": "Соняшник", "en": "Sunflower"},
        "aliases": ["соняшник", "helianthus"],
        "images": [],
        "popularity": 10,
    },
    {
        "id": "pl_wheat",
        "name": {"uk": "Пшениця", "en": "Wheat"},
        "aliases": ["пшениця", "triticum"],
        "images": [],
        "popularity": 9,
    },
    {
        "id": "pl_soy",
        "name": {"uk": "Соя", "en": "Soybean"},
        "aliases": ["соя", "glycine max"],
        "images": [],
        "popularity": 7,
    },
]

diseases = [
    {
        "id": "dis_sclerotinia",
        "plant_id": "pl_sunflower",
        "name": {"uk": "Склеротинія", "en": "Sclerotinia"},
        "symptoms": ["в'янення", "біла гниль", "склероції"],
        "causes": "Sclerotinia sclerotiorum",
        "treatments": [
            {"type": "organic", "title": "Сівозміна"},
            {"type": "chemical", "title": "Фунгіцид"},
        ],
        "gallery": [],
        "popularity": 10,
    },
    {
        "id": "dis_rust",
        "plant_id": "pl_wheat",
        "name": {"uk": "Іржа пшениці", "en": "Wheat Rust"},
        "symptoms": ["пустули іржі", "зниження врожайності"],
        "causes": "Puccinia spp.",
        "treatments": [{"type": "chemical", "title": "Фунгіцид (сторбілурини)"}],
        "gallery": [],
        "popularity": 8,
    },
    {
        "id": "dis_fusarium",
        "plant_id": "pl_soy",
        "name": {"uk": "Фузаріоз", "en": "Fusarium"},
        "symptoms": ["коренева гниль", "в'янення"],
        "causes": "Fusarium spp.",
        "treatments": [
            {"type": "organic", "title": "Сівозміна"},
            {"type": "chemical", "title": "Фунгіцид"},
        ],
        "gallery": [],
        "popularity": 7,
    },
]


async def main():
    await init_db()
    await Plant.delete_all()
    await Disease.delete_all()
    await Plant.insert_many([Plant(**p) for p in plants])
    await Disease.insert_many([Disease(**d) for d in diseases])
    print("Seeded plants & diseases")


if __name__ == "__main__":
    asyncio.run(main())
