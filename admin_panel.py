import sqlite3
from datetime import datetime
import json

def get_db_connection():
    """Получение соединения с базой данных"""
    conn = sqlite3.connect('bot_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_component(name, category_id, price, price_category_id, description="", specs=None, image_url=None):
    """Добавление нового компонента"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Преобразуем спецификации в JSON, если они переданы
    specs_json = json.dumps(specs) if specs else None
    
    cursor.execute("""
        INSERT INTO components (name, category_id, price, price_category_id, description, specs, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, category_id, price, price_category_id, description, specs_json, image_url))
    
    component_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return component_id

def add_build(name, device_type_id, price_category_id, description="", component_ids=None, image_url=None):
    """Добавление новой сборки"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Рассчитываем общую стоимость сборки на основе компонентов
    total_price = 0
    if component_ids:
        # Получаем цены компонентов
        placeholders = ','.join(['?'] * len(component_ids))
        components = conn.execute(f"""
            SELECT id, price FROM components 
            WHERE id IN ({placeholders})
        """, component_ids).fetchall()
        
        total_price = sum(component["price"] for component in components)
    
    # Добавляем сборку
    cursor.execute("""
        INSERT INTO pc_builds (name, device_type_id, price_category_id, total_price, description, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, device_type_id, price_category_id, total_price, description, image_url))
    
    build_id = cursor.lastrowid
    
    # Добавляем связи сборки с компонентами
    if component_ids:
        for component_id in component_ids:
            cursor.execute("""
                INSERT INTO build_components (build_id, component_id)
                VALUES (?, ?)
            """, (build_id, component_id))
    
    conn.commit()
    conn.close()
    return build_id

def update_price_category(category_id, name, min_price, max_price, description):
    """Обновление ценовой категории"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE price_categories 
        SET name = ?, min_price = ?, max_price = ?, description = ?
        WHERE id = ?
    """, (name, min_price, max_price, description, category_id))
    
    conn.commit()
    conn.close()

def get_all_components():
    """Получение списка всех компонентов"""
    conn = get_db_connection()
    components = conn.execute("""
        SELECT c.*, cc.name as category_name, pc.name as price_category_name 
        FROM components c
        JOIN component_categories cc ON c.category_id = cc.id
        JOIN price_categories pc ON c.price_category_id = pc.id
        ORDER BY c.name
    """).fetchall()
    conn.close()
    return [dict(row) for row in components]

def get_all_builds():
    """Получение списка всех сборок"""
    conn = get_db_connection()
    builds = conn.execute("""
        SELECT b.*, dt.name as device_type_name, pc.name as price_category_name 
        FROM pc_builds b
        JOIN device_types dt ON b.device_type_id = dt.id
        JOIN price_categories pc ON b.price_category_id = pc.id
        ORDER BY b.name
    """).fetchall()
    conn.close()
    return [dict(row) for row in builds]

def get_component_categories():
    """Получение списка категорий компонентов"""
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM component_categories ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in categories]

def get_device_types():
    """Получение списка типов устройств"""
    conn = get_db_connection()
    types = conn.execute("SELECT * FROM device_types ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in types]

def get_price_categories():
    """Получение списка ценовых категорий"""
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM price_categories ORDER BY min_price").fetchall()
    conn.close()
    return [dict(row) for row in categories]

# Пример использования:
if __name__ == "__main__":
    # Пример добавления компонента
    new_component = add_component(
        name="Intel Core i5-12400F",
        category_id=1,  # Процессоры
        price=15990,
        price_category_id=2,  # Средний
        description="6-ядерный процессор для игр и работы",
        specs={
            "Ядра": "6",
            "Потоки": "12",
            "Частота": "2.5-4.4 GHz"
        }
    )
    print(f"Добавлен новый компонент с ID: {new_component}")
    
    # Пример добавления сборки
    new_build = add_build(
        name="Игровой ПК Старт",
        device_type_id=1,  # Игровой ПК
        price_category_id=2,  # Средний
        description="Базовая игровая сборка",
        component_ids=[new_component]  # ID добавленного компонента
    )
    print(f"Добавлена новая сборка с ID: {new_build}")
    
    # Пример обновления ценовой категории
    update_price_category(
        category_id=1,
        name="Бюджетный",
        min_price=0,
        max_price=40000,
        description="Недорогие решения до 40 тыс. рублей"
    )
    print("Ценовая категория обновлена")
    
    # Вывод списков
    print("\nСписок компонентов:")
    for component in get_all_components():
        print(f"{component['id']}: {component['name']} - {component['price']} руб.")
    
    print("\nСписок сборок:")
    for build in get_all_builds():
        print(f"{build['id']}: {build['name']} - {build['total_price']} руб.") 