from database import get_builds_by_type_and_price, get_price_categories, get_device_types

# Получаем все типы устройств и ценовые категории

def main():
    device_types = get_device_types()
    price_categories = get_price_categories()
    print("Список сборок в базе данных:\n")
    for device in device_types:
        for price_cat in price_categories:
            builds = get_builds_by_type_and_price(device['id'], price_cat['id'])
            if not builds:
                continue
            print(f"Тип устройства: {device['name']} | Категория: {price_cat['name']}")
            for build in builds:
                print(f"  id: {build['id']}, Название: {build['name']}, Цена: {build['total_price']} руб.")
                if build.get('link'):
                    print(f"    Ссылка: {build['link']}")
            print()

if __name__ == "__main__":
    main() 