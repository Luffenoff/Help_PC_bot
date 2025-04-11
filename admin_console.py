from admin_panel import *
import json

def print_menu():
    print("\n=== Административная панель ===")
    print("1. Добавить компонент")
    print("2. Добавить сборку")
    print("3. Обновить ценовую категорию")
    print("4. Просмотреть все компоненты")
    print("5. Просмотреть все сборки")
    print("6. Просмотреть категории компонентов")
    print("7. Просмотреть типы устройств")
    print("8. Просмотреть ценовые категории")
    print("0. Выход")
    return input("Выберите действие: ")

def add_component_console():
    print("\n=== Добавление нового компонента ===")
    
    # Показываем доступные категории
    categories = get_component_categories()
    print("\nДоступные категории:")
    for cat in categories:
        print(f"{cat['id']}. {cat['name']}")
    category_id = int(input("\nВыберите категорию (ID): "))
    
    # Показываем ценовые категории
    price_categories = get_price_categories()
    print("\nДоступные ценовые категории:")
    for pc in price_categories:
        print(f"{pc['id']}. {pc['name']} ({pc['min_price']}-{pc['max_price']} руб.)")
    price_category_id = int(input("\nВыберите ценовую категорию (ID): "))
    
    name = input("Название компонента: ")
    price = int(input("Цена (руб.): "))
    description = input("Описание (Enter для пропуска): ")
    
    # Спецификации
    specs = {}
    print("\nВведите спецификации (оставьте поле пустым для завершения):")
    while True:
        key = input("Название характеристики: ")
        if not key:
            break
        value = input("Значение: ")
        specs[key] = value
    
    image_url = input("URL изображения (Enter для пропуска): ")
    
    component_id = add_component(
        name=name,
        category_id=category_id,
        price=price,
        price_category_id=price_category_id,
        description=description,
        specs=specs if specs else None,
        image_url=image_url if image_url else None
    )
    
    print(f"\nКомпонент успешно добавлен с ID: {component_id}")

def add_build_console():
    print("\n=== Добавление новой сборки ===")
    
    # Показываем типы устройств
    device_types = get_device_types()
    print("\nДоступные типы устройств:")
    for dt in device_types:
        print(f"{dt['id']}. {dt['name']}")
    device_type_id = int(input("\nВыберите тип устройства (ID): "))
    
    # Показываем ценовые категории
    price_categories = get_price_categories()
    print("\nДоступные ценовые категории:")
    for pc in price_categories:
        print(f"{pc['id']}. {pc['name']} ({pc['min_price']}-{pc['max_price']} руб.)")
    price_category_id = int(input("\nВыберите ценовую категорию (ID): "))
    
    name = input("Название сборки: ")
    description = input("Описание (Enter для пропуска): ")
    
    # Выбор компонентов
    components = get_all_components()
    print("\nДоступные компоненты:")
    for comp in components:
        print(f"{comp['id']}. {comp['name']} - {comp['price']} руб.")
    
    component_ids = []
    print("\nВведите ID компонентов (по одному, Enter для завершения):")
    while True:
        comp_id = input("ID компонента: ")
        if not comp_id:
            break
        component_ids.append(int(comp_id))
    
    image_url = input("URL изображения (Enter для пропуска): ")
    
    build_id = add_build(
        name=name,
        device_type_id=device_type_id,
        price_category_id=price_category_id,
        description=description,
        component_ids=component_ids,
        image_url=image_url if image_url else None
    )
    
    print(f"\nСборка успешно добавлена с ID: {build_id}")

def update_price_category_console():
    print("\n=== Обновление ценовой категории ===")
    
    categories = get_price_categories()
    print("\nДоступные ценовые категории:")
    for cat in categories:
        print(f"{cat['id']}. {cat['name']} ({cat['min_price']}-{cat['max_price']} руб.)")
    
    category_id = int(input("\nВыберите категорию для обновления (ID): "))
    name = input("Новое название: ")
    min_price = int(input("Минимальная цена: "))
    max_price = int(input("Максимальная цена: "))
    description = input("Описание: ")
    
    update_price_category(
        category_id=category_id,
        name=name,
        min_price=min_price,
        max_price=max_price,
        description=description
    )
    
    print("\nЦеновая категория успешно обновлена")

def print_components():
    print("\n=== Список компонентов ===")
    components = get_all_components()
    for comp in components:
        print(f"\nID: {comp['id']}")
        print(f"Название: {comp['name']}")
        print(f"Категория: {comp['category_name']}")
        print(f"Ценовая категория: {comp['price_category_name']}")
        print(f"Цена: {comp['price']} руб.")
        print(f"Описание: {comp['description']}")
        if comp['specs']:
            print("Спецификации:")
            specs = json.loads(comp['specs'])
            for key, value in specs.items():
                print(f"  {key}: {value}")

def print_builds():
    print("\n=== Список сборок ===")
    builds = get_all_builds()
    for build in builds:
        print(f"\nID: {build['id']}")
        print(f"Название: {build['name']}")
        print(f"Тип устройства: {build['device_type_name']}")
        print(f"Ценовая категория: {build['price_category_name']}")
        print(f"Общая стоимость: {build['total_price']} руб.")
        print(f"Описание: {build['description']}")

def print_categories():
    print("\n=== Категории компонентов ===")
    categories = get_component_categories()
    for cat in categories:
        print(f"{cat['id']}. {cat['name']} - {cat['description']}")

def print_device_types():
    print("\n=== Типы устройств ===")
    types = get_device_types()
    for dt in types:
        print(f"{dt['id']}. {dt['name']} - {dt['description']}")

def print_price_categories():
    print("\n=== Ценовые категории ===")
    categories = get_price_categories()
    for cat in categories:
        print(f"{cat['id']}. {cat['name']} ({cat['min_price']}-{cat['max_price']} руб.) - {cat['description']}")

def main():
    while True:
        choice = print_menu()
        
        if choice == "1":
            add_component_console()
        elif choice == "2":
            add_build_console()
        elif choice == "3":
            update_price_category_console()
        elif choice == "4":
            print_components()
        elif choice == "5":
            print_builds()
        elif choice == "6":
            print_categories()
        elif choice == "7":
            print_device_types()
        elif choice == "8":
            print_price_categories()
        elif choice == "0":
            print("Выход из программы")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main() 