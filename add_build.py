from builds_links import BuildLinkManager
import json

def main():
    manager = BuildLinkManager()
    
    print("Добавление новой сборки")
    print("=====================")
    
    # Получаем шаблон
    build_data = manager.get_build_template()
    
    # Заполняем основные данные
    build_data["name"] = input("Название сборки: ")
    print("\nДоступные типы устройств:")
    print("1. Игровой ПК")
    print("2. Рабочий ПК")
    print("3. Ноутбук")
    device_type = input("Выберите тип устройства (1-3): ")
    build_data["device_type"] = ["игровой ПК", "рабочий ПК", "ноутбук"][int(device_type)-1]
    
    print("\nДоступные ценовые категории:")
    print("1. Дешево")
    print("2. Средне")
    print("3. Дорого")
    price_cat = input("Выберите ценовую категорию (1-3): ")
    build_data["price_category"] = ["дешево", "средне", "дорого"][int(price_cat)-1]
    
    build_data["description"] = input("\nОписание сборки: ")
    build_data["image_url"] = input("Ссылка на изображение (опционально): ")
    
    # Добавляем компоненты
    components = []
    while True:
        print("\nДобавление компонента")
        print("-------------------")
        component = {
            "name": input("Название компонента: "),
            "category": input("Категория компонента: "),
            "price": int(input("Цена: ")),
            "link": input("Ссылка на компонент: "),
            "description": input("Описание компонента: ")
        }
        components.append(component)
        
        if input("\nДобавить еще компонент? (y/n): ").lower() != 'y':
            break
    
    build_data["components"] = components
    
    # Сохраняем в файл
    filename = f"build_{build_data['name'].lower().replace(' ', '_')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(build_data, f, ensure_ascii=False, indent=4)
    
    print(f"\nДанные сохранены в файл {filename}")
    
    # Добавляем сборку в базу
    success, message = manager.add_build_from_link(build_data)
    print(f"\n{message}")

if __name__ == "__main__":
    main() 