import re
import json
from database import add_component, add_build, get_component_categories, get_price_categories

# Категории компонентов по ключевым словам
CATEGORY_KEYWORDS = {
    1: ["процессор"],
    2: ["видеокарта"],
    3: ["оперативная память", "озу"],
    4: ["накопитель", "жесткий диск", "ssd", "hdd"],
    5: ["материнская плата"],
    6: ["блок питания"],
    7: ["кулер", "охлаждение"],
    8: ["корпус"],
}

# Получить id категории по названию компонента
def get_category_id(name):
    name = name.lower()
    for cat_id, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                return cat_id
    return None

# Определить ценовую категорию по цене
PRICE_CATEGORIES = [
    (1, 0, 40000),
    (2, 40000, 80000),
    (3, 80000, 500000),
]
def get_price_category_id(price):
    for cat_id, min_p, max_p in PRICE_CATEGORIES:
        if min_p <= price <= max_p:
            return cat_id
    return 1

# Парсинг файла

def parse_sborki(filename):
    with open(filename, encoding="utf-8") as f:
        text = f.read()
    # Разделяем по номеру и ссылке
    blocks = re.split(r"\n\d+\.https?://", text)
    links = re.findall(r"\d+\.(https?://[\w\-./]+)", text)
    builds = []
    for i, block in enumerate(blocks[1:]):
        link = links[i] if i < len(links) else None
        # Название сборки
        name_match = re.search(r"Процессор ([^\n]+)", block)
        name = f"Сборка {i+1}"
        if name_match:
            name = f"{name_match.group(1).strip()} сборка #{i+1}"
        # Общая цена
        price_match = re.search(r"(\d{2,3} \d{3}) ₽", block)
        total_price = int(price_match.group(1).replace(" ", "")) if price_match else 0
        # Описание
        description = f"Импортировано из sborki.txt. Ссылка: {link}"
        # Парсим компоненты
        comp_lines = re.findall(r"([А-Яа-яA-Za-z0-9 \-\[\]().,:]+)\n[Вв] наличии|([А-Яа-яA-Za-z0-9 \-\[\]().,:]+)\nЗаменить", block)
        components = []
        for c1, c2 in comp_lines:
            cname = c1 or c2
            if not cname: continue
            cat_id = get_category_id(cname)
            if not cat_id: continue
            # Цена компонента
            price = 0
            price_match = re.search(re.escape(cname) + r".*?(\d{1,3} \d{3}) ₽", block, re.DOTALL)
            if price_match:
                price = int(price_match.group(1).replace(" ", ""))
            components.append({
                "name": cname.strip(),
                "category_id": cat_id,
                "price": price,
                "description": cname.strip(),
                "specs": None
            })
        builds.append({
            "name": name,
            "link": link,
            "total_price": total_price,
            "description": description,
            "components": components
        })
    return builds

def main():
    builds = parse_sborki("sborki.txt")
    for build in builds:
        component_ids = []
        for comp in build["components"]:
            price_cat_id = get_price_category_id(comp["price"])
            comp_id = add_component(
                name=comp["name"],
                category_id=comp["category_id"],
                price=comp["price"],
                price_category_id=price_cat_id,
                description=comp["description"],
                specs=comp["specs"],
                image_url=None
            )
            component_ids.append(comp_id)
        # Определяем ценовую категорию сборки
        build_price_cat = get_price_category_id(build["total_price"])
        add_build(
            name=build["name"],
            device_type_id=1,  # Игровой ПК
            price_category_id=build_price_cat,
            description=build["description"],
            component_ids=component_ids,
            image_url=None,
            link=build["link"]
        )
    print("Импорт сборок завершён!")

if __name__ == "__main__":
    main() 