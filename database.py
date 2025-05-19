import sqlite3
import json
from datetime import datetime
import random

DATABASE_FILE = "bot_database.db"

def get_db_connection():
    """Получение соединения с базой данных"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация базы данных и создание необходимых таблиц"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица для пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        registration_date TEXT,
        last_active TEXT
    )
    ''')
    
    # Таблица для типов устройств (игровой ПК, рабочий ПК, ноутбук)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS device_types (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )
    ''')
    
    # Таблица для ценовых категорий (дешево, средне, дорого)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        min_price INTEGER,
        max_price INTEGER,
        description TEXT
    )
    ''')
    
    # Таблица для категорий компонентов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS component_categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )
    ''')
    
    # Таблица для компьютерных комплектующих
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS components (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category_id INTEGER,
        price_category_id INTEGER,
        price INTEGER,
        description TEXT,
        specs TEXT,
        image_url TEXT,
        FOREIGN KEY (category_id) REFERENCES component_categories (id),
        FOREIGN KEY (price_category_id) REFERENCES price_categories (id)
    )
    ''')
    
    # Таблица для готовых сборок
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pc_builds (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        device_type_id INTEGER,
        price_category_id INTEGER,
        total_price INTEGER,
        description TEXT,
        image_url TEXT,
        link TEXT,
        FOREIGN KEY (device_type_id) REFERENCES device_types (id),
        FOREIGN KEY (price_category_id) REFERENCES price_categories (id)
    )
    ''')
    
    # Таблица для связи сборок и компонентов (many-to-many)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS build_components (
        id INTEGER PRIMARY KEY,
        build_id INTEGER,
        component_id INTEGER,
        FOREIGN KEY (build_id) REFERENCES pc_builds (id),
        FOREIGN KEY (component_id) REFERENCES components (id)
    )
    ''')
    
    # Таблица для хранения ссылок и текста страниц
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS page_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        page_text TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Таблица для предложений пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        suggestion_text TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT
    )
    ''')
    
    # Проверяем, нужно ли заполнить типы устройств
    cursor.execute("SELECT COUNT(*) FROM device_types")
    if cursor.fetchone()[0] == 0:
        device_types = [
            (1, "Игровой ПК", "Компьютеры для игр с высокой производительностью"),
            (2, "Офисный ПК", "Компьютеры для работы и офисного использования")
        ]
        cursor.executemany("INSERT INTO device_types (id, name, description) VALUES (?, ?, ?)", device_types)
    
    # Проверяем, нужно ли заполнить ценовые категории
    cursor.execute("SELECT COUNT(*) FROM price_categories")
    if cursor.fetchone()[0] == 0:
        price_categories = [
            (1, "Бюджетный", 0, 40000, "Недорогие решения до 40 тыс. рублей"),
            (2, "Средний", 40000, 80000, "Сбалансированные решения от 40 до 80 тыс. рублей"),
            (3, "Премиум", 80000, 500000, "Высокопроизводительные системы от 80 тыс. рублей")
        ]
        cursor.executemany("INSERT INTO price_categories (id, name, min_price, max_price, description) VALUES (?, ?, ?, ?, ?)", price_categories)
    
    # Проверяем, нужно ли заполнить категории компонентов
    cursor.execute("SELECT COUNT(*) FROM component_categories")
    if cursor.fetchone()[0] == 0:
        component_categories = [
            (1, "Процессоры", "Центральные процессоры (CPU)"),
            (2, "Видеокарты", "Графические процессоры (GPU)"),
            (3, "Оперативная память", "Модули памяти (RAM)"),
            (4, "Накопители", "SSD и HDD накопители"),
            (5, "Материнские платы", "Системные платы"),
            (6, "Блоки питания", "Источники питания (PSU)"),
            (7, "Охлаждение", "Системы охлаждения компонентов"),
            (8, "Корпуса", "Компьютерные корпуса")
        ]
        cursor.executemany("INSERT INTO component_categories (id, name, description) VALUES (?, ?, ?)", component_categories)
    
    conn.commit()
    conn.close()
    print("База данных инициализирована: bot_database.db")
    
    # Инициализируем базовые данные
    init_basic_data()
    
    # Исправляем ценовые категории
    fix_price_categories()

def update_user_last_active(user_id):
    """Обновление времени последней активности пользователя"""
    conn = get_db_connection()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (current_time, user_id))
    conn.commit()
    conn.close()

def get_device_types():
    """Получение всех типов устройств"""
    conn = get_db_connection()
    device_types = conn.execute("SELECT * FROM device_types").fetchall()
    conn.close()
    return [dict(row) for row in device_types]

def get_price_categories():
    """Получение всех ценовых категорий"""
    conn = get_db_connection()
    price_categories = conn.execute("SELECT * FROM price_categories").fetchall()
    conn.close()
    return [dict(row) for row in price_categories]

def get_component_categories():
    """Получение всех категорий компонентов"""
    conn = get_db_connection()
    component_categories = conn.execute("SELECT * FROM component_categories").fetchall()
    conn.close()
    return [dict(row) for row in component_categories]

def get_builds_by_type_and_price(device_type_id, price_category_id):
    """Получение сборок по типу устройства и ценовой категории"""
    conn = get_db_connection()
    builds = conn.execute("""
        SELECT * FROM pc_builds 
        WHERE device_type_id = ? AND price_category_id = ?
    """, (device_type_id, price_category_id)).fetchall()
    conn.close()
    return [dict(row) for row in builds]

def get_build_details(build_id):
    """Получение детальной информации о сборке, включая компоненты"""
    conn = get_db_connection()
    build = conn.execute("SELECT * FROM pc_builds WHERE id = ?", (build_id,)).fetchone()
    
    if not build:
        conn.close()
        return None
    
    # Получаем компоненты, связанные с этой сборкой
    components = conn.execute("""
        SELECT c.* FROM components c
        JOIN build_components bc ON c.id = bc.component_id
        WHERE bc.build_id = ?
    """, (build_id,)).fetchall()
    
    conn.close()
    
    return {
        "build": dict(build),
        "components": [dict(component) for component in components]
    }

def get_components_by_category(category_id):
    """Получение компонентов по категории"""
    conn = get_db_connection()
    components = conn.execute("""
        SELECT * FROM components 
        WHERE category_id = ?
        ORDER BY price
    """, (category_id,)).fetchall()
    conn.close()
    return [dict(row) for row in components]

def get_components_by_category_and_price(category_id, price_category_id):
    """Получение компонентов по категории и ценовой категории"""
    conn = get_db_connection()
    components = conn.execute("""
        SELECT * FROM components 
        WHERE category_id = ? AND price_category_id = ?
        ORDER BY price
    """, (category_id, price_category_id)).fetchall()
    conn.close()
    return [dict(row) for row in components]

def get_component_details(component_id):
    """Получение детальной информации о компоненте"""
    conn = get_db_connection()
    component = conn.execute("SELECT * FROM components WHERE id = ?", (component_id,)).fetchone()
    conn.close()
    
    if not component:
        return None
    
    result = dict(component)
    
    # Преобразуем JSON строку спецификаций в словарь, если она есть
    if result["specs"] and result["specs"].strip():
        try:
            result["specs"] = json.loads(result["specs"])
        except json.JSONDecodeError:
            # Если не удалось разобрать JSON, оставляем как есть
            pass
    
    return result

# Функции для добавления тестовых данных (используются для разработки)

def add_component(name, category_id, price, price_category_id, description="", specs=None, image_url=None):
    """Добавление компонента в базу данных"""
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

def add_build(name, device_type_id, price_category_id, description="", component_ids=None, image_url=None, link=None):
    """Добавление сборки в базу данных"""
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
    
    # Получаем границы ценовой категории
    cursor.execute("SELECT min_price, max_price FROM price_categories WHERE id = ?", (price_category_id,))
    price_range = cursor.fetchone()
    
    if price_range and (total_price < price_range["min_price"] or total_price > price_range["max_price"]):
        # Если цена не соответствует категории, выбираем правильную категорию
        cursor.execute("""
            SELECT id FROM price_categories 
            WHERE min_price <= ? AND max_price >= ?
            ORDER BY min_price
            LIMIT 1
        """, (total_price, total_price))
        correct_category = cursor.fetchone()
        if correct_category:
            price_category_id = correct_category["id"]
    
    # Добавляем сборку
    cursor.execute("""
        INSERT INTO pc_builds (name, device_type_id, price_category_id, total_price, description, image_url, link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, device_type_id, price_category_id, total_price, description, image_url, link))
    
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

def add_test_data():
    """Добавление тестовых данных в базу данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Добавляем тестовые сборки
    test_builds = [
        (1, "Игровой ПК начального уровня", 1, 1, 35000, "Бюджетный игровой ПК для начинающих", None, "https://example.com/build1"),
        (2, "Игровой ПК среднего уровня", 1, 2, 60000, "Сбалансированный игровой ПК", None, "https://example.com/build2"),
        (3, "Игровой ПК премиум", 1, 3, 120000, "Мощный игровой ПК", None, "https://example.com/build3"),
        (4, "Рабочий ПК начального уровня", 2, 1, 30000, "Бюджетный ПК для офиса", None, "https://example.com/build4"),
        (5, "Рабочий ПК среднего уровня", 2, 2, 50000, "Сбалансированный рабочий ПК", None, "https://example.com/build5"),
        (6, "Рабочий ПК премиум", 2, 3, 100000, "Мощный рабочий ПК", None, "https://example.com/build6"),
        (7, "Ноутбук начального уровня", 3, 1, 40000, "Бюджетный ноутбук", None, "https://example.com/build7"),
        (8, "Ноутбук среднего уровня", 3, 2, 70000, "Сбалансированный ноутбук", None, "https://example.com/build8"),
        (9, "Ноутбук премиум", 3, 3, 150000, "Мощный ноутбук", None, "https://example.com/build9")
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO pc_builds 
        (id, name, device_type_id, price_category_id, total_price, description, image_url, link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, test_builds)
    
    conn.commit()
    conn.close()
    print("Тестовые данные добавлены в базу данных")

def get_random_build(device_type_id, price_category_id) -> dict:
    """Получение случайной сборки со всеми компонентами"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем случайную сборку с учетом типа устройства и ценовой категории
    cursor.execute("""
        SELECT id, name, device_type_id, price_category_id, total_price, description, link
        FROM pc_builds
        WHERE device_type_id = ? AND price_category_id = ?
        ORDER BY RANDOM()
        LIMIT 1
    """, (device_type_id, price_category_id))
    build = cursor.fetchone()
    
    if not build:
        conn.close()
        return None
    
    # Получаем компоненты сборки
    cursor.execute("""
        SELECT c.*, cc.name as category_name
        FROM components c
        JOIN build_components bc ON c.id = bc.component_id
        JOIN component_categories cc ON c.category_id = cc.id
        WHERE bc.build_id = ?
    """, (build[0],))
    
    components = cursor.fetchall()
    conn.close()
    
    # Формируем результат
    result = {
        'id': build[0],
        'name': build[1],
        'device_type_id': build[2],
        'price_category_id': build[3],
        'total_price': build[4],
        'description': build[5],
        'link': build[6],
        'components': []
    }
    
    # Добавляем компоненты
    for component in components:
        specs = json.loads(component['specs']) if component['specs'] else None
        result['components'].append({
            'id': component['id'],
            'name': component['name'],
            'category': component['category_name'],
            'price': component['price'],
            'description': component['description'],
            'specs': specs
        })
    
    return result

def add_page_data(url: str, page_text: str) -> int:
    """Добавление новой записи с ссылкой и текстом страницы"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO page_data (url, page_text) VALUES (?, ?)",
        (url, page_text)
    )
    page_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return page_id

def get_page_data(page_id: int) -> dict:
    """Получение данных страницы по ID"""
    conn = get_db_connection()
    page = conn.execute("SELECT * FROM page_data WHERE id = ?", (page_id,)).fetchone()
    conn.close()
    return dict(page) if page else None

def get_all_page_data() -> list:
    """Получение всех записей страниц"""
    conn = get_db_connection()
    pages = conn.execute("SELECT * FROM page_data ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(page) for page in pages]

def search_page_data(query: str) -> list:
    """Поиск по тексту страниц"""
    conn = get_db_connection()
    pages = conn.execute(
        "SELECT * FROM page_data WHERE page_text LIKE ? OR url LIKE ? ORDER BY created_at DESC",
        (f"%{query}%", f"%{query}%")
    ).fetchall()
    conn.close()
    return [dict(page) for page in pages]


def init_basic_data():
    """Инициализация базовых данных (категории, типы устройств, ценовые категории)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже данные в таблице device_types
    cursor.execute("SELECT COUNT(*) FROM device_types")
    if cursor.fetchone()[0] == 0:
        # Добавляем типы устройств только если таблица пуста
        device_types = [
            (1, "Игровой ПК", "Компьютеры для игр с высокой производительностью"),
            (2, "Офисный ПК", "Компьютеры для работы и офисного использования")
        ]
        cursor.executemany("""
            INSERT INTO device_types (id, name, description)
            VALUES (?, ?, ?)
        """, device_types)
    
    # Проверяем, есть ли уже данные в таблице price_categories
    cursor.execute("SELECT COUNT(*) FROM price_categories")
    if cursor.fetchone()[0] == 0:
        # Добавляем ценовые категории только если таблица пуста
        price_categories = [
            (1, "Бюджетный", 0, 40000, "Недорогие решения до 40 тыс. рублей"),
            (2, "Средний", 40000, 80000, "Сбалансированные решения от 40 до 80 тыс. рублей"),
            (3, "Премиум", 80000, 500000, "Высокопроизводительные системы от 80 тыс. рублей")
        ]
        cursor.executemany("""
            INSERT INTO price_categories (id, name, min_price, max_price, description)
            VALUES (?, ?, ?, ?, ?)
        """, price_categories)
    
    # Проверяем, есть ли уже данные в таблице component_categories
    cursor.execute("SELECT COUNT(*) FROM component_categories")
    if cursor.fetchone()[0] == 0:
        # Добавляем категории компонентов только если таблица пуста
        component_categories = [
            (1, "Процессоры", "Центральные процессоры (CPU)"),
            (2, "Видеокарты", "Графические процессоры (GPU)"),
            (3, "Оперативная память", "Модули памяти (RAM)"),
            (4, "Накопители", "SSD и HDD накопители"),
            (5, "Материнские платы", "Системные платы"),
            (6, "Блоки питания", "Источники питания (PSU)"),
            (7, "Охлаждение", "Системы охлаждения компонентов"),
            (8, "Корпуса", "Компьютерные корпуса")
        ]
        cursor.executemany("""
            INSERT INTO component_categories (id, name, description)
            VALUES (?, ?, ?)
        """, component_categories)
    
    conn.commit()
    conn.close()
    print("Базовые данные инициализированы")

def delete_build(build_id):
    """Удаление сборки из базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Удаляем связи сборки с компонентами
    cursor.execute("DELETE FROM build_components WHERE build_id = ?", (build_id,))
    
    # Удаляем саму сборку
    cursor.execute("DELETE FROM pc_builds WHERE id = ?", (build_id,))
    
    conn.commit()
    conn.close()

def fix_price_categories():
    """Исправление ценовых категорий для существующих сборок"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем все сборки
    cursor.execute("SELECT id, total_price FROM pc_builds")
    builds = cursor.fetchall()
    
    # Для каждой сборки проверяем и исправляем ценовую категорию
    for build in builds:
        # Находим подходящую ценовую категорию
        cursor.execute("""
            SELECT id FROM price_categories 
            WHERE min_price <= ? AND max_price >= ?
            ORDER BY min_price
            LIMIT 1
        """, (build["total_price"], build["total_price"]))
        correct_category = cursor.fetchone()
        
        if correct_category:
            # Обновляем ценовую категорию сборки
            cursor.execute("""
                UPDATE pc_builds 
                SET price_category_id = ? 
                WHERE id = ?
            """, (correct_category["id"], build["id"]))
    
    conn.commit()
    conn.close()
    print("Ценовые категории сборок исправлены")

def copy_components_from_builds():
    """Копирование компонентов из сборок в таблицу компонентов"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем все сборки
    cursor.execute("SELECT id FROM pc_builds")
    builds = cursor.fetchall()
    
    for build in builds:
        build_id = build[0]
        # Получаем компоненты сборки
        cursor.execute("""
            SELECT c.* FROM components c
            JOIN build_components bc ON c.id = bc.component_id
            WHERE bc.build_id = ?
        """, (build_id,))
        components = cursor.fetchall()
        
        # Для каждого компонента проверяем, есть ли он уже в таблице components
        for component in components:
            cursor.execute("""
                SELECT id FROM components 
                WHERE name = ? AND category_id = ? AND price_category_id = ?
            """, (component['name'], component['category_id'], component['price_category_id']))
            existing = cursor.fetchone()
            
            if not existing:
                # Если компонента нет, добавляем его
                cursor.execute("""
                    INSERT INTO components (name, category_id, price_category_id, price, description, specs, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    component['name'],
                    component['category_id'],
                    component['price_category_id'],
                    component['price'],
                    component['description'],
                    component['specs'],
                    component['image_url']
                ))
    
    conn.commit()
    conn.close()

def add_suggestion(user_id: int, suggestion_text: str) -> int:
    """Добавляет новое предложение от пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO suggestions (user_id, suggestion_text) VALUES (?, ?)",
        (user_id, suggestion_text)
    )
    suggestion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return suggestion_id

def get_user_suggestions(user_id: int) -> list:
    """Получает все предложения пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM suggestions WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    suggestions = cursor.fetchall()
    conn.close()
    return suggestions

def get_all_suggestions() -> list:
    """Получает все предложения для администратора"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.*, u.username, u.first_name, u.last_name 
        FROM suggestions s 
        JOIN users u ON s.user_id = u.user_id 
        ORDER BY s.created_at DESC
        """
    )
    suggestions = cursor.fetchall()
    conn.close()
    return suggestions

def update_suggestion_status(suggestion_id: int, status: str) -> bool:
    """Обновляет статус предложения"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE suggestions SET status = ? WHERE id = ?",
        (status, suggestion_id)
    )
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

# Инициализация БД при импорте модуля
init_db()