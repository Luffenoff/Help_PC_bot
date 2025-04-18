from database import (
    add_build,
    get_device_types,
    get_price_categories,
    get_component_categories
)

def print_menu(title, items):
    print(f"\n{title}:")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item['name']}")

def add_build_manual():
    print("Добавление новой сборки ПК")
    print("=========================")
    
    # Получаем список типов устройств
    device_types = get_device_types()
    print_menu("Типы устройств", device_types)
    device_type_id = int(input("Выберите тип устройства (1-3): "))
    
    # Получаем список ценовых категорий
    price_categories = get_price_categories()
    print_menu("Ценовые категории", price_categories)
    price_category_id = int(input("Выберите ценовую категорию (1-3): "))
    
    # Вводим основную информацию о сборке
    name = input("\nНазвание сборки: ")
    description = input("Описание сборки: ")
    image_url = input("Ссылка на изображение (опционально): ")
    
    # Вводим компоненты
    components = []
    while True:
        print("\nДобавление компонента")
        print("-------------------")
        
        # Получаем список категорий компонентов
        categories = get_component_categories()
        print_menu("Категории компонентов", categories)
        category_id = int(input("Выберите категорию компонента: "))
        
        component_name = input("Название компонента: ")
        price = int(input("Цена компонента: "))
        specs = {}
        
        # Вводим характеристики компонента
        print("\nВведите характеристики компонента (для завершения введите пустую строку):")
        while True:
            spec_name = input("Название характеристики: ")
            if not spec_name:
                break
            spec_value = input("Значение характеристики: ")
            specs[spec_name] = spec_value
        
        components.append({
            "name": component_name,
            "category_id": category_id,
            "price": price,
            "specs": specs
        })
        
        if input("\nДобавить еще компонент? (y/n): ").lower() != 'y':
            break
    
    # Добавляем сборку в базу данных
    build_id = add_build(
        name=name,
        device_type_id=device_type_id,
        price_category_id=price_category_id,
        description=description,
        component_ids=[c["category_id"] for c in components],
        image_url=image_url
    )
    
    print(f"\nСборка успешно добавлена с ID: {build_id}")
    print("Компоненты сборки:")
    for component in components:
        print(f"\n{component['name']} ({component['price']} руб.)")
        print("Характеристики:")
        for spec_name, spec_value in component['specs'].items():
            print(f"- {spec_name}: {spec_value}")

if __name__ == "__main__":
    add_build_manual() 