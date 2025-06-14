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
        link TEXT,
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

def bulk_add_processors():
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("Intel Core i3-10105 BOX", 1, 0, 1, "Современный процессор для офисных и домашних ПК", "https://www.dns-shop.ru/product/182b754efc02ed20/processor-intel-core-i3-10105-box/"),
        ("AMD Ryzen 9 7900X3D BOX", 1, 0, 3, "Топовый процессор для игровых и рабочих станций", "https://www.dns-shop.ru/product/3e574ae0e4a5ed20/processor-amd-ryzen-9-7900x3d-box/"),
        ("Intel Core i9-10900F OEM", 1, 0, 3, "Мощный 10-ядерный процессор для энтузиастов", "https://www.dns-shop.ru/product/e9f5ca4c6a673332/processor-intel-core-i9-10900f-oem/"),
        ("AMD Ryzen 9 7900 OEM", 1, 0, 3, "Высокопроизводительный процессор для demanding задач", "https://www.dns-shop.ru/product/8cb25d34e95ded20/processor-amd-ryzen-9-7900-oem/"),
        ("AMD Ryzen 7 8700G OEM", 1, 0, 2, "Процессор с мощной встроенной графикой", "https://www.dns-shop.ru/product/e210c892aec6ed20/processor-amd-ryzen-7-8700g-oem/"),
        ("Intel Core i7-12700F OEM", 1, 0, 2, "12-ядерный процессор для универсальных задач", "https://www.dns-shop.ru/product/9cbce4510180ed20/processor-intel-core-i7-12700f-oem/"),
        ("Intel Core i9-12900K OEM", 1, 0, 3, "Флагманский процессор Intel 12-го поколения", "https://www.dns-shop.ru/product/b1479f2ffccaed20/processor-intel-core-i9-12900k-oem/"),
        ("AMD Ryzen 7 5800X OEM", 1, 0, 2, "8-ядерный процессор для игр и работы", "https://www.dns-shop.ru/product/4e48fbd4fb77ed20/processor-amd-ryzen-7-5800x-oem/"),
        ("AMD Ryzen 5 7600X BOX", 1, 0, 2, "Процессор нового поколения для универсальных ПК", "https://www.dns-shop.ru/product/2134060338aeed20/processor-amd-ryzen-5-7600x-box/"),
        ("AMD Ryzen 5 5600GT OEM", 1, 0, 1, "Бюджетный 6-ядерный процессор", "https://www.dns-shop.ru/product/7ab10bfaa543ed20/processor-amd-ryzen-5-5600gt-oem/"),
        ("Intel Core i3-10105 OEM", 1, 0, 1, "Доступный процессор для офисных задач", "https://www.dns-shop.ru/product/78f8884016f4ed20/processor-intel-core-i3-10105-oem/"),
        ("Intel Core i9-14900KF OEM", 1, 0, 3, "Флагманский процессор Intel 14-го поколения", "https://www.dns-shop.ru/product/011cda247238ed20/processor-intel-core-i9-14900kf-oem/"),
        ("AMD Ryzen 5 7400F OEM", 1, 0, 1, "Современный 6-ядерный процессор", "https://www.dns-shop.ru/product/9a818bb1d39cd9cb/processor-amd-ryzen-5-7400f-oem/"),
        ("Intel Core i5-12600K OEM", 1, 0, 2, "Процессор для универсальных и игровых ПК", "https://www.dns-shop.ru/product/f6f618bafc03ed20/processor-intel-core-i5-12600k-oem/"),
        ("Intel Core i7-13700K OEM", 1, 0, 3, "Мощный процессор для энтузиастов", "https://www.dns-shop.ru/product/1e48b8b03f94ed20/processor-intel-core-i7-13700k-oem/"),
        ("AMD Ryzen 5 3600 OEM", 1, 0, 1, "Популярный 6-ядерный процессор", "https://www.dns-shop.ru/product/39783e4afccbed20/processor-amd-ryzen-5-3600-oem/"),
        ("Intel Core i9-14900K OEM", 1, 0, 3, "Флагманский процессор Intel 14-го поколения", "https://www.dns-shop.ru/product/4400b6287237ed20/processor-intel-core-i9-14900k-oem/"),
        ("AMD Ryzen 9 9950X OEM", 1, 0, 3, "Топовый процессор для рабочих станций", "https://www.dns-shop.ru/product/b28701d724a2d582/processor-amd-ryzen-9-9950x-oem/"),
        ("Intel Core i7-12700KF OEM", 1, 0, 2, "12-ядерный процессор для универсальных задач", "https://www.dns-shop.ru/product/9525d6f70717ed20/processor-intel-core-i7-12700kf-oem/"),
        ("AMD Ryzen 9 9950X3D OEM", 1, 0, 3, "Процессор с 3D V-Cache для максимальной производительности", "https://www.dns-shop.ru/product/4b4450decf2bd582/processor-amd-ryzen-9-9950x3d-oem/"),
        ("AMD Ryzen 5 7600 OEM", 1, 0, 2, "6-ядерный процессор нового поколения", "https://www.dns-shop.ru/product/93478ee7e957ed20/processor-amd-ryzen-5-7600-oem/"),
        ("AMD Ryzen 3 3200G OEM", 1, 0, 1, "Бюджетный процессор с графикой Vega", "https://www.dns-shop.ru/product/588277aa3347ed20/processor-amd-ryzen-3-3200g-oem/"),
        ("Intel Core i5-12400F OEM", 1, 0, 2, "6-ядерный процессор для универсальных ПК", "https://www.dns-shop.ru/product/0a2114a7fcc9ed20/processor-intel-core-i5-12400f-oem/"),
        ("Intel Core i5-13400F OEM", 1, 0, 2, "10-ядерный процессор для универсальных ПК", "https://www.dns-shop.ru/product/641859136153d715/processor-intel-core-i5-13400f-oem/"),
        ("AMD Ryzen 7 5700X OEM", 1, 0, 2, "8-ядерный процессор для игр и работы", "https://www.dns-shop.ru/product/96054164afeaed20/processor-amd-ryzen-7-5700x-oem/"),
        ("AMD Ryzen 7 9800X3D OEM", 1, 0, 3, "Процессор с 3D V-Cache для игр и рабочих задач", "https://www.dns-shop.ru/product/104767799cdfd582/processor-amd-ryzen-7-9800x3d-oem/"),
        ("AMD Ryzen 7 7800X3D OEM", 1, 0, 3, "Процессор с 3D V-Cache для максимальной производительности", "https://www.dns-shop.ru/product/3ecad0b7a46fed20/processor-amd-ryzen-7-7800x3d-oem/"),
        ("AMD Ryzen 5 7500F OEM", 1, 0, 1, "Современный 6-ядерный процессор", "https://www.dns-shop.ru/product/d4bde9994d11ed20/processor-amd-ryzen-5-7500f-oem/")
    ]
    cursor.executemany("INSERT INTO components (name, category_id, price, price_category_id, description, link) VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def update_processor_descriptions():
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    # Список универсальных описаний по ключевым словам в названии
    updates = [
        ("i3-10105", "4 ядра, 8 потоков, частота до 4.4 ГГц, сокет LGA1200. Отличный выбор для офисных и домашних ПК."),
        ("i9-10900F", "10 ядер, 20 потоков, частота до 5.2 ГГц, сокет LGA1200. Для энтузиастов и рабочих станций."),
        ("i9-12900K", "16 ядер (8P+8E), 24 потока, частота до 5.2 ГГц, сокет LGA1700. Флагман для игр и работы."),
        ("i9-14900K", "24 ядра (8P+16E), 32 потока, частота до 6.0 ГГц, сокет LGA1700. Максимальная производительность."),
        ("i9-14900KF", "24 ядра (8P+16E), 32 потока, частота до 6.0 ГГц, сокет LGA1700. Максимальная производительность."),
        ("i7-12700F", "12 ядер (8P+4E), 20 потоков, частота до 4.9 ГГц, сокет LGA1700. Универсальный выбор для игр и работы."),
        ("i7-12700KF", "12 ядер (8P+4E), 20 потоков, частота до 5.0 ГГц, сокет LGA1700. Универсальный выбор для игр и работы."),
        ("i7-13700K", "16 ядер (8P+8E), 24 потока, частота до 5.4 ГГц, сокет LGA1700. Для энтузиастов и игр."),
        ("i5-12400F", "6 ядер, 12 потоков, частота до 4.4 ГГц, сокет LGA1700. Отлично подходит для универсальных ПК."),
        ("i5-12600K", "10 ядер (6P+4E), 16 потоков, частота до 4.9 ГГц, сокет LGA1700. Для игр и работы."),
        ("i5-13400F", "10 ядер (6P+4E), 16 потоков, частота до 4.6 ГГц, сокет LGA1700. Универсальный процессор."),
        ("Ryzen 9 7900X3D", "12 ядер, 24 потока, частота до 5.6 ГГц, сокет AM5. Топ для игр и рабочих задач."),
        ("Ryzen 9 7900", "12 ядер, 24 потока, частота до 5.4 ГГц, сокет AM5. Для demanding задач."),
        ("Ryzen 9 9950X3D", "16 ядер, 32 потока, частота до 5.7 ГГц, сокет AM5. Максимальная производительность."),
        ("Ryzen 9 9950X", "16 ядер, 32 потока, частота до 5.7 ГГц, сокет AM5. Максимальная производительность."),
        ("Ryzen 7 8700G", "8 ядер, 16 потоков, частота до 5.1 ГГц, сокет AM5, мощная встроенная графика."),
        ("Ryzen 7 5800X", "8 ядер, 16 потоков, частота до 4.7 ГГц, сокет AM4. Для игр и работы."),
        ("Ryzen 7 5700X", "8 ядер, 16 потоков, частота до 4.6 ГГц, сокет AM4. Для игр и работы."),
        ("Ryzen 7 7800X3D", "8 ядер, 16 потоков, частота до 5.0 ГГц, сокет AM5, 3D V-Cache. Для игр."),
        ("Ryzen 7 9800X3D", "8 ядер, 16 потоков, частота до 5.5 ГГц, сокет AM5, 3D V-Cache. Для игр."),
        ("Ryzen 5 7600X", "6 ядер, 12 потоков, частота до 5.3 ГГц, сокет AM5. Универсальный процессор."),
        ("Ryzen 5 7600", "6 ядер, 12 потоков, частота до 5.1 ГГц, сокет AM5. Универсальный процессор."),
        ("Ryzen 5 7500F", "6 ядер, 12 потоков, частота до 5.0 ГГц, сокет AM5. Для игр и работы."),
        ("Ryzen 5 7400F", "6 ядер, 12 потоков, частота до 4.7 ГГц, сокет AM5. Для игр и работы."),
        ("Ryzen 5 5600GT", "6 ядер, 12 потоков, частота до 4.6 ГГц, сокет AM4. Бюджетный вариант."),
        ("Ryzen 5 3600", "6 ядер, 12 потоков, частота до 4.2 ГГц, сокет AM4. Популярный выбор."),
        ("Ryzen 3 3200G", "4 ядра, 4 потока, частота до 4.0 ГГц, сокет AM4, встроенная графика Vega.")
    ]
    for key, desc in updates:
        cursor.execute("UPDATE components SET description = ? WHERE name LIKE ?", (desc, f"%{key}%"))
    conn.commit()
    conn.close()

def bulk_add_motherboards():
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("MSI B650M GAMING PLUS WIFI", 5, 0, 2, "Материнская плата на чипсете B650, сокет AM5, поддержка DDR5, M.2, Wi-Fi. Для современных процессоров AMD Ryzen.", "https://www.dns-shop.ru/product/77439794ba6ded20/materinskaa-plata-msi-b650m-gaming-plus-wifi/"),
        ("MSI PRO B650-S WIFI", 5, 0, 2, "Материнская плата на чипсете B650, сокет AM5, поддержка DDR5, Wi-Fi. Для AMD Ryzen 7000/8000.", "https://www.dns-shop.ru/product/7d98e5645604ed20/materinskaa-plata-msi-pro-b650-s-wifi/"),
        ("MSI PRO H610M-E DDR4", 5, 0, 1, "Материнская плата на чипсете H610, сокет LGA1700, поддержка DDR4, M.2. Для процессоров Intel 12/13/14 поколения.", "https://www.dns-shop.ru/product/56027c0307e7ed20/materinskaa-plata-msi-pro-h610m-e-ddr4/"),
        ("MSI B850 GAMING PLUS WIFI", 5, 0, 3, "Материнская плата на чипсете B850, сокет AM5, поддержка DDR5, Wi-Fi. Для топовых сборок AMD.", "https://www.dns-shop.ru/product/ec6a873ec35ed582/materinskaa-plata-msi-b850-gaming-plus-wifi/"),
        ("MSI PRO Z790-P WIFI", 5, 0, 3, "Материнская плата на чипсете Z790, сокет LGA1700, поддержка DDR5, Wi-Fi. Для процессоров Intel Core 12/13/14 Gen.", "https://www.dns-shop.ru/product/56ba7ffc4e03ed20/materinskaa-plata-msi-pro-z790-p-wifi/"),
        ("MSI PRO B650M-P", 5, 0, 2, "Материнская плата на чипсете B650, сокет AM5, поддержка DDR5, M.2. Для AMD Ryzen 7000/8000.", "https://www.dns-shop.ru/product/2a63664ce255ed20/materinskaa-plata-msi-pro-b650m-p/"),
        ("MSI MAG X870 TOMAHAWK WIFI", 5, 0, 3, "Материнская плата на чипсете X870, сокет AM5, поддержка DDR5, Wi-Fi. Для топовых процессоров AMD Ryzen.", "https://www.dns-shop.ru/product/2012b1a27a16d582/materinskaa-plata-msi-mag-x870-tomahawk-wifi/"),
        ("MSI PRO H610M-E", 5, 0, 1, "Материнская плата на чипсете H610, сокет LGA1700, поддержка DDR4. Для офисных и домашних ПК на Intel.", "https://www.dns-shop.ru/product/a5c3a9774ddfed20/materinskaa-plata-msi-pro-h610m-e/"),
        ("MSI PRO B760M-P", 5, 0, 2, "Материнская плата на чипсете B760, сокет LGA1700, поддержка DDR4, M.2. Для современных процессоров Intel.", "https://www.dns-shop.ru/product/7155ab10d2caed20/materinskaa-plata-msi-pro-b760m-p/"),
        ("ASUS PRIME B550M-A", 5, 0, 2, "Материнская плата на чипсете B550, сокет AM4, поддержка DDR4, M.2. Для AMD Ryzen 3000/5000.", "https://www.dns-shop.ru/product/a3504362a6df3332/materinskaa-plata-asus-prime-b550m-a/"),
        ("MSI A520M PRO", 5, 0, 1, "Материнская плата на чипсете A520, сокет AM4, поддержка DDR4. Для бюджетных сборок AMD Ryzen.", "https://www.dns-shop.ru/product/52ff1f19ba132eb1/materinskaa-plata-msi-a520m-pro/"),
        ("ASRock H370M-HDV", 5, 0, 1, "Материнская плата на чипсете H370, сокет LGA1151, поддержка DDR4. Для процессоров Intel 8/9 Gen.", "https://www.dns-shop.ru/product/6cb131492f8b3332/materinskaa-plata-asrock-h370m-hdv/"),
        ("ASRock B760M-HDV/M.2 D4", 5, 0, 2, "Материнская плата на чипсете B760, сокет LGA1700, поддержка DDR4, M.2. Для Intel 12/13/14 Gen.", "https://www.dns-shop.ru/product/8aa9c1bb9590ed20/materinskaa-plata-asrock-b760m-hdvm2-d4/"),
        ("GIGABYTE B550I AORUS PRO AX", 5, 0, 3, "Компактная материнская плата ITX на чипсете B550, сокет AM4, поддержка DDR4, Wi-Fi. Для компактных сборок AMD.", "https://www.dns-shop.ru/product/4f3c4a329c061b80/materinskaa-plata-gigabyte-b550i-aorus-pro-ax/"),
        ("MSI B550-A PRO", 5, 0, 2, "Материнская плата на чипсете B550, сокет AM4, поддержка DDR4, M.2. Для AMD Ryzen 3000/5000.", "https://www.dns-shop.ru/product/232aa9fbb9a11b80/materinskaa-plata-msi-b550-a-pro/"),
        ("ASUS TUF GAMING B760-PLUS WIFI", 5, 0, 2, "Материнская плата на чипсете B760, сокет LGA1700, поддержка DDR4, Wi-Fi. Для игровых и универсальных ПК на Intel.", "https://www.dns-shop.ru/product/02b7d698ab7ced20/materinskaa-plata-asus-tuf-gaming-b760-plus-wifi/"),
        ("MSI PRO B760M-A DDR4 II", 5, 0, 2, "Материнская плата на чипсете B760, сокет LGA1700, поддержка DDR4, M.2. Для современных процессоров Intel.", "https://www.dns-shop.ru/product/f83aa9e8cedbed20/materinskaa-plata-msi-pro-b760m-a-ddr4-ii/")
    ]
    cursor.executemany("INSERT INTO components (name, category_id, price, price_category_id, description, link) VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def bulk_add_gpus():
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("Sapphire AMD Radeon RX 550 Pulse OC", 2, 0, 1, "Видеокарта на чипе RX 550, 4 ГБ GDDR5, HDMI, DVI, компактная и энергоэффективная. Для офисных и мультимедийных ПК.", "https://www.dns-shop.ru/product/6af1cb5a28903330/videokarta-sapphire-amd-radeon-rx-550-pulse-oc-11268-01-20g/"),
        ("MSI GeForce 210 N210-1GD3LP", 2, 0, 1, "Базовая видеокарта для офисных ПК и мультимедиа, 1 ГБ DDR3, DVI, VGA, HDMI.", "https://www.dns-shop.ru/product/5a7b4c6d0bc3c823/videokarta-msi-geforce-210-n210-1gd3lp/"),
        ("ASRock AMD Radeon RX 6500 XT Phantom Gaming", 2, 0, 2, "Видеокарта на чипе RX 6500 XT, 8 ГБ GDDR6, HDMI, DisplayPort. Для современных игр в Full HD.", "https://www.dns-shop.ru/product/8dacf9c25863d582/videokarta-asrock-amd-radeon-rx-6500-xt-phantom-gaming-rx6500xt-pg-8go/"),
        ("Gigabyte GeForce RTX 5060 Ti Windforce OC", 2, 0, 3, "Видеокарта на чипе RTX 5060 Ti, 16 ГБ GDDR6, HDMI, DisplayPort. Для требовательных игр и работы.", "https://www.dns-shop.ru/product/a48b10d205f8d9cb/videokarta-gigabyte-geforce-rtx-5060-ti-windforce-oc-gv-n506twf2oc-16gd/"),
        ("MSI GeForce RTX 5080 Gaming Trio", 2, 0, 3, "Топовая видеокарта RTX 5080, 16 ГБ GDDR6X, HDMI, DisplayPort. Для 4K-гейминга и рабочих станций.", "https://www.dns-shop.ru/product/d383d3c705fed582/videokarta-msi-geforce-rtx-5080-gaming-trio-rtx-5080-16g-gaming-trio/"),
        ("Gigabyte GeForce RTX 3060 Gaming OC", 2, 0, 2, "Видеокарта на чипе RTX 3060, 8 ГБ GDDR6, HDMI, DisplayPort. Для современных игр в Full HD и QHD.", "https://www.dns-shop.ru/product/7a50a72f1321d582/videokarta-gigabyte-geforce-rtx-3060-gaming-oc-rev-20-gv-n3060gaming-oc-8gd-20/"),
        ("ASRock AMD Radeon RX 550 Phantom Gaming", 2, 0, 1, "Видеокарта на чипе RX 550, 4 ГБ GDDR5, HDMI, DVI. Для офисных и мультимедийных ПК.", "https://www.dns-shop.ru/product/30020ef93a8bed20/videokarta-asrock-amd-radeon-rx-550-phantom-gaming-phantom-g-r-rx550-4g/"),
        ("KFA2 GeForce GT 710", 2, 0, 1, "Базовая видеокарта для офисных ПК, 2 ГБ DDR3, DVI, VGA, HDMI.", "https://www.dns-shop.ru/product/975c271ba7781b80/videokarta-kfa2-geforce-gt-710-71gpf4hi00gk/"),
        ("Gigabyte GeForce RTX 5070 Aero OC", 2, 0, 3, "Видеокарта на чипе RTX 5070, 12 ГБ GDDR6X, HDMI, DisplayPort. Для требовательных игр и работы.", "https://www.dns-shop.ru/product/198854d2d4b8d582/videokarta-gigabyte-geforce-rtx-5070-aero-oc-gv-n5070aero-oc-12gd/"),
        ("ASRock AMD Radeon RX 6500 XT Phantom Gaming D OC", 2, 0, 2, "Видеокарта на чипе RX 6500 XT, 4 ГБ GDDR6, HDMI, DisplayPort. Для современных игр в Full HD.", "https://www.dns-shop.ru/product/fa9a78b683fded20/videokarta-asrock-amd-radeon-rx-6500-xt-phantom-gaming-d-oc-rx6500xt-pgd-4go/"),
        ("Palit GeForce RTX 4070 Super Dual", 2, 0, 3, "Видеокарта на чипе RTX 4070 Super, 12 ГБ GDDR6X, HDMI, DisplayPort. Для игр в QHD и 4K.", "https://www.dns-shop.ru/product/a941a417a2e4ed20/videokarta-palit-geforce-rtx-4070-super-dual-ned407s019k9-1043d/"),
        ("KFA2 GeForce RTX 3050 X Black", 2, 0, 2, "Видеокарта на чипе RTX 3050, 8 ГБ GDDR6, HDMI, DisplayPort. Для Full HD-гейминга.", "https://www.dns-shop.ru/product/5a74a34171b1ed20/videokarta-kfa2-geforce-rtx-3050-x-black-35nsl8md6yek/"),
        ("ASRock AMD Radeon RX 6600 Challenger D", 2, 0, 2, "Видеокарта на чипе RX 6600, 8 ГБ GDDR6, HDMI, DisplayPort. Для современных игр в Full HD.", "https://www.dns-shop.ru/product/4bb4202e5d77ed20/videokarta-asrock-amd-radeon-rx-6600-challenger-d-rx6600-cld-8g/"),
        ("Palit GeForce RTX 5070 GamingPro", 2, 0, 3, "Видеокарта на чипе RTX 5070, 12 ГБ GDDR6X, HDMI, DisplayPort. Для требовательных игр и работы.", "https://www.dns-shop.ru/product/db789f5be780d582/videokarta-palit-geforce-rtx-5070-gamingpro-ne75070019k9-gb2050a/"),
        ("Palit GeForce RTX 4060 Infinity 2", 2, 0, 2, "Видеокарта на чипе RTX 4060, 8 ГБ GDDR6, HDMI, DisplayPort. Для современных игр в Full HD и QHD.", "https://www.dns-shop.ru/product/c455f512e73aed20/videokarta-palit-geforce-rtx-4060-infinity-2-ne64060019p1-1070l/"),
        ("Palit GeForce RTX 5070 Infinity 3", 2, 0, 3, "Видеокарта на чипе RTX 5070, 12 ГБ GDDR6X, HDMI, DisplayPort. Для требовательных игр и работы.", "https://www.dns-shop.ru/product/b58aaa7e00a9d582/videokarta-palit-geforce-rtx-5070-infinity-3-ne75070019k9-gb2050s/"),
        ("MSI GeForce RTX 3050 Gaming X", 2, 0, 2, "Видеокарта на чипе RTX 3050, 8 ГБ GDDR6, HDMI, DisplayPort. Для Full HD-гейминга.", "https://www.dns-shop.ru/product/a1560975bc27ed20/videokarta-msi-geforce-rtx-3050-gaming-x-912-v812-024/")
    ]
    cursor.executemany("INSERT INTO components (name, category_id, price, price_category_id, description, link) VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def bulk_add_ram():
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("Kingston FURY Beast Black RGB KF556C36BBEAK2-32 32 ГБ", 3, 0, 2, "DDR5, 32 ГБ (2x16 ГБ), 5600 МГц, RGB-подсветка, поддержка XMP. Для современных игровых и рабочих ПК.", "https://www.dns-shop.ru/product/82dbb4b53960ed20/operativnaa-pamat-kingston-fury-beast-black-rgb-kf556c36bbeak2-32-32-gb/"),
        ("ADATA XPG Lancer AX5U6000C3032G-DCLABK 64 ГБ", 3, 0, 3, "DDR5, 64 ГБ (2x32 ГБ), 6000 МГц, поддержка XMP. Для топовых игровых и рабочих станций.", "https://www.dns-shop.ru/product/65fdeb5051f8ed20/operativnaa-pamat-adata-xpg-lancer-ax5u6000c3032g-dclabk-64-gb/"),
        ("ADATA XPG Lancer Blade AX5U6000C3032G-DTLABBK 64 ГБ", 3, 0, 3, "DDR5, 64 ГБ (2x32 ГБ), 6000 МГц, низкопрофильный радиатор, поддержка XMP.", "https://www.dns-shop.ru/product/b100b98851fded20/operativnaa-pamat-adata-xpg-lancer-blade-ax5u6000c3032g-dtlabbk-64-gb/"),
        ("ADATA XPG GAMMIX D35 AX4U320016G16A-DTWHD35 32 ГБ", 3, 0, 2, "DDR4, 32 ГБ (2x16 ГБ), 3200 МГц, поддержка XMP. Универсальный выбор для апгрейда.", "https://www.dns-shop.ru/product/d3054d361638ed20/operativnaa-pamat-adata-xpg-gammix-d35-ax4u320016g16a-dtwhd35-32-gb/"),
        ("G.Skill Aegis F4-3200C16D-16GIS 16 ГБ", 3, 0, 1, "DDR4, 16 ГБ (2x8 ГБ), 3200 МГц, поддержка XMP. Для офисных и домашних ПК.", "https://www.dns-shop.ru/product/2117ec86c6aded20/operativnaa-pamat-gskill-aegis-f4-3200c16d-16gis-16-gb/"),
        ("G.Skill Trident Z5 RGB F5-6000J3040F16GX2-TZ5RK 32 ГБ", 3, 0, 3, "DDR5, 32 ГБ (2x16 ГБ), 6000 МГц, RGB, поддержка XMP. Для топовых игровых ПК.", "https://www.dns-shop.ru/product/c6ac4ce2bbcded20/operativnaa-pamat-gskill-trident-z5-rgb-f5-6000j3040f16gx2-tz5rk-32-gb/"),
        ("Kingston FURY Beast Black RGB KF556C40BBAK2-64 64 ГБ", 3, 0, 3, "DDR5, 64 ГБ (2x32 ГБ), 5600 МГц, RGB, поддержка XMP. Для рабочих станций и энтузиастов.", "https://www.dns-shop.ru/product/94bab109f078ed20/operativnaa-pamat-kingston-fury-beast-black-rgb-kf556c40bbak2-64-64-gb/"),
        ("ADATA XPG GAMMIX D20 AX4U320032G16A-DCBK20 64 ГБ", 3, 0, 2, "DDR4, 64 ГБ (2x32 ГБ), 3200 МГц, поддержка XMP. Для мощных рабочих ПК.", "https://www.dns-shop.ru/product/35e0980fea98d763/operativnaa-pamat-adata-xpg-gammix-d20-ax4u320032g16a-dcbk20-64-gb/"),
        ("Kingston FURY Beast Black KF556C40BBK2-32 32 ГБ", 3, 0, 2, "DDR5, 32 ГБ (2x16 ГБ), 5600 МГц, поддержка XMP. Для современных ПК.", "https://www.dns-shop.ru/product/e47d2e94faeaed20/operativnaa-pamat-kingston-fury-beast-black-kf556c40bbk2-32-32-gb/"),
        ("ADATA XPG GAMMIX D20 AX4U32008G16A-DCBK20 16 ГБ", 3, 0, 1, "DDR4, 16 ГБ (2x8 ГБ), 3200 МГц, поддержка XMP. Для офисных и домашних ПК.", "https://www.dns-shop.ru/product/f5054e5aea99d763/operativnaa-pamat-adata-xpg-gammix-d20-ax4u32008g16a-dcbk20-16-gb/"),
        ("Kingston FURY Beast Black KF432C16BB1K232 32 ГБ", 3, 0, 2, "DDR4, 32 ГБ (2x16 ГБ), 3200 МГц, поддержка XMP. Универсальный выбор для апгрейда.", "https://www.dns-shop.ru/product/3f208dfc2f3ded20/operativnaa-pamat-kingston-fury-beast-black-kf432c16bb1k232-32-gb/"),
        ("G.Skill Aegis F4-3200C16D-32GIS 32 ГБ", 3, 0, 2, "DDR4, 32 ГБ (2x16 ГБ), 3200 МГц, поддержка XMP. Для универсальных и игровых ПК.", "https://www.dns-shop.ru/product/90af6f65c774ed20/operativnaa-pamat-gskill-aegis-f4-3200c16d-32gis-32-gb/"),
        ("ADATA XPG Lancer Blade AX5U6400C3216G-DTLABBK 32 ГБ", 3, 0, 2, "DDR5, 32 ГБ (2x16 ГБ), 6400 МГц, низкопрофильный радиатор, поддержка XMP.", "https://www.dns-shop.ru/product/d3fa71f65849ed20/operativnaa-pamat-adata-xpg-lancer-blade-ax5u6400c3216g-dtlabbk-32-gb/"),
        ("Kingston FURY Beast Black KF552C40BBK2-32 32 ГБ", 3, 0, 2, "DDR5, 32 ГБ (2x16 ГБ), 5200 МГц, поддержка XMP. Для современных ПК.", "https://www.dns-shop.ru/product/720699befaeaed20/operativnaa-pamat-kingston-fury-beast-black-kf552c40bbk2-32-32-gb/"),
        ("Kingston FURY Beast Black KF432C16BBK264 64 ГБ", 3, 0, 2, "DDR4, 64 ГБ (2x32 ГБ), 3200 МГц, поддержка XMP. Для рабочих станций и энтузиастов.", "https://www.dns-shop.ru/product/a3191630faebed20/operativnaa-pamat-kingston-fury-beast-black-kf432c16bbk264-64-gb/"),
        ("Kingston FURY Beast Black KF432C16BBK216 16 ГБ", 3, 0, 1, "DDR4, 16 ГБ (2x8 ГБ), 3200 МГц, поддержка XMP. Для офисных и домашних ПК.", "https://www.dns-shop.ru/product/bb6fb3a7fad5ed20/operativnaa-pamat-kingston-fury-beast-black-kf432c16bbk216-16-gb/"),
        ("Kingston FURY Beast Black KF432C16BBK232 32 ГБ", 3, 0, 2, "DDR4, 32 ГБ (2x16 ГБ), 3200 МГц, поддержка XMP. Универсальный выбор для апгрейда.", "https://www.dns-shop.ru/product/9ed60ce7fae5ed20/operativnaa-pamat-kingston-fury-beast-black-kf432c16bbk232-32-gb/"),
        ("Kingston FURY Beast Black KF556C36BBEK2-32 32 ГБ", 3, 0, 2, "DDR5, 32 ГБ (2x16 ГБ), 5600 МГц, поддержка XMP. Для современных ПК.", "https://www.dns-shop.ru/product/17e2942c3953ed20/operativnaa-pamat-kingston-fury-beast-black-kf556c36bbek2-32-32-gb/")
    ]
    cursor.executemany("INSERT INTO components (name, category_id, price, price_category_id, description, link) VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def bulk_add_coolers():
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("ID-COOLING SE-224-XTS ARGB", 7, 0, 2, "Кулер для процессора, 4 тепловые трубки, ARGB-подсветка, поддержка LGA1700/AM4. Эффективное и тихое охлаждение.", "https://www.dns-shop.ru/product/5e2127f83401ed20/kuler-dla-processora-id-cooling-se-224-xts-argb/"),
        ("Deepcool AG620 R AG620-BKNNMN-G-1", 7, 0, 2, "Кулер для процессора, 6 тепловых трубок, двойной вентилятор, поддержка LGA1700/AM4. Для мощных процессоров.", "https://www.dns-shop.ru/product/f2c7e6bcea8aed20/kuler-dla-processora-deepcool-ag620-r-ag620-bknnmn-g-1/"),
        ("Deepcool AK620 LGA1700 R AK620-BKNMMT-G", 7, 0, 2, "Кулер для процессора, 6 тепловых трубок, двойной вентилятор, поддержка LGA1700/AM4. Высокая эффективность охлаждения.", "https://www.dns-shop.ru/product/f65523875885ed20/kuler-dla-processora-deepcool-ak620-lga1700-r-ak620-bknnmt-g/"),
        ("ID-COOLING SE-903-XT BLACK", 7, 0, 1, "Компактный кулер для процессора, 3 тепловые трубки, поддержка LGA1700/AM4. Для офисных и домашних ПК.", "https://www.dns-shop.ru/product/4202bd74ae7eed20/kuler-dla-processora-id-cooling-se-903-xt-black-se-903-xt-black/"),
        ("Deepcool AK620 Digital R AK620-BKADMN-G", 7, 0, 3, "Кулер для процессора, цифровой дисплей, 6 тепловых трубок, двойной вентилятор, поддержка LGA1700/AM4.", "https://www.dns-shop.ru/product/e82b1b28efb5ed20/kuler-dla-processora-deepcool-ak620-digital-r-ak620-bkadmn-g/"),
        ("Deepcool AG400 R AG400-BKNNMN-G-1", 7, 0, 1, "Кулер для процессора, 4 тепловые трубки, поддержка LGA1700/AM4. Универсальный выбор для апгрейда.", "https://www.dns-shop.ru/product/3f6f629ce633ed20/kuler-dla-processora-deepcool-ag400-r-ag400-bknnmn-g-1/"),
        ("Deepcool AG620 Digital R AG620-BKNDMN-G-1", 7, 0, 3, "Кулер для процессора, цифровой дисплей, 6 тепловых трубок, двойной вентилятор, поддержка LGA1700/AM4.", "https://www.dns-shop.ru/product/e1b7c2736cb9ed20/kuler-dla-processora-deepcool-ag620-digital-r-ag620-bkndmn-g-1/"),
        ("ID-COOLING SE-225-XT BLACK V2 LGA1700", 7, 0, 2, "Кулер для процессора, 4 тепловые трубки, поддержка LGA1700/AM4. Эффективное охлаждение.", "https://www.dns-shop.ru/product/dab64ee34cbaed20/kuler-dla-processora-id-cooling-se-225-xt-black-v2-lga1700-se-225-xt-black/"),
        ("ID-COOLING SE-903-SD V3", 7, 0, 1, "Компактный кулер для процессора, 3 тепловые трубки, поддержка LGA1700/AM4. Для офисных и домашних ПК.", "https://www.dns-shop.ru/product/a4ed23b64d53ed20/kuler-dla-processora-id-cooling-se-903-sd-v3/"),
        ("Deepcool AK400 Digital R AK400-BKADMN-G", 7, 0, 2, "Кулер для процессора, цифровой дисплей, 4 тепловые трубки, поддержка LGA1700/AM4.", "https://www.dns-shop.ru/product/c48a5501efb4ed20/kuler-dla-processora-deepcool-ak400-digital-r-ak400-bkadmn-g/"),
        ("MSI MAG CORELIQUID E360 White", 7, 0, 3, "СЖО, радиатор 360 мм, ARGB, поддержка современных сокетов. Для мощных игровых и рабочих ПК.", "https://www.dns-shop.ru/product/d5fb1e9a02e2d582/sistema-ohlazdenia-msi-mag-coreliquid-e360-white/"),
        ("ID-COOLING DASHFLOW 240 BASIC BLACK", 7, 0, 2, "СЖО, радиатор 240 мм, ARGB, поддержка современных сокетов. Для игровых и рабочих ПК.", "https://www.dns-shop.ru/product/0b6ca609536aed20/sistema-ohlazdenia-id-cooling-dashflow-240-basic-black/"),
        ("ID-COOLING SL360 XE", 7, 0, 3, "СЖО, радиатор 360 мм, ARGB, поддержка современных сокетов. Для мощных процессоров.", "https://www.dns-shop.ru/product/489b7b0bc0bfed20/sistema-ohlazdenia-id-cooling-sl360-xe/"),
        ("Lian Li Galahad II Trinity 360 SL-INF", 7, 0, 3, "СЖО, радиатор 360 мм, ARGB, поддержка современных сокетов. Для топовых игровых и рабочих ПК.", "https://www.dns-shop.ru/product/12b266444ae1ed20/sistema-ohlazdenia-lian-li-galahad-ii-trinity-360-sl-inf/"),
        ("Deepcool LE520", 7, 0, 2, "СЖО, радиатор 240 мм, ARGB, поддержка современных сокетов. Для игровых и рабочих ПК.", "https://www.dns-shop.ru/product/79e0c1e2e3f8ed20/sistema-ohlazdenia-deepcool-le520/"),
        ("Arctic Cooling Liquid Freezer III 360 A-RGB", 7, 0, 3, "СЖО, радиатор 360 мм, ARGB, поддержка современных сокетов. Для мощных процессоров.", "https://www.dns-shop.ru/product/6ab1c1cb72005ecf/sistema-ohlazdenia-arctic-cooling-liquid-freezer-iii-360-a-rgb/"),
        ("MSI MEG CORELIQUID S360", 7, 0, 3, "СЖО, радиатор 360 мм, ARGB, поддержка современных сокетов. Для топовых игровых и рабочих ПК.", "https://www.dns-shop.ru/product/d36de8b0f8efd763/sistema-ohlazdenia-msi-meg-coreliquid-s360/"),
        ("MSI MAG CORELIQUID E360", 7, 0, 3, "СЖО, радиатор 360 мм, ARGB, поддержка современных сокетов. Для мощных игровых и рабочих ПК.", "https://www.dns-shop.ru/product/487c25b102e2d582/sistema-ohlazdenia-msi-mag-coreliquid-e360/")
    ]
    cursor.executemany("INSERT INTO components (name, category_id, price, price_category_id, description, link) VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def bulk_add_office_pcs():
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("Мини ПК Acer Gadget E10 ETBox", 2, 0, 1, "Intel Core i5-12450H, 16 ГБ DDR5, SSD 512 ГБ, Windows 11 Pro, DisplayPort, HDMI, VGA, Wi-Fi, Bluetooth, блок питания 120 Вт.", "https://www.dns-shop.ru/product/1bf47191dc70d9cb/mini-pk-acer-gadget-e10-etbox-1746843/"),
        ("ПК DEXP Atlas H494", 2, 0, 1, "Intel Core i3-12100, 8 ГБ DDR4, SSD 256 ГБ, без ОС, HDMI, VGA, Intel H610, блок питания 350 Вт.", "https://www.dns-shop.ru/product/fb7372ffa6ecd582/pk-dexp-atlas-h494/"),
        ("Мини ПК Chuwi UBox", 2, 0, 1, "AMD Ryzen 5 6600H, 16 ГБ DDR5, SSD 512 ГБ, Windows 11 Pro, DisplayPort, HDMI, Wi-Fi, Bluetooth, блок питания 90 Вт.", "https://www.dns-shop.ru/product/1032684d843fd582/mini-pk-chuwi-ubox-1746526/"),
        ("Мини ПК DEXP Mini Entry (8/256)", 2, 0, 1, "Intel N100, 8 ГБ DDR4, SSD 256 ГБ, Windows 11 Pro, 2 x HDMI, Wi-Fi, Bluetooth, блок питания 36 Вт.", "https://www.dns-shop.ru/product/80c17395c6c1eed8/mini-pk-dexp-mini-entry/"),
        ("Мини ПК DEXP Mini Entry (16/512)", 2, 0, 1, "Intel N100, 16 ГБ DDR4, SSD 512 ГБ, Windows 11 Pro, 2 x HDMI, Wi-Fi, Bluetooth, блок питания 36 Вт.", "https://www.dns-shop.ru/product/e10bde6713a607a3/mini-pk-dexp-mini-entry/"),
        ("Мини ПК DEXP Mini Smart BM002", 2, 0, 1, "Intel Core i5-1235U, 16 ГБ DDR4, SSD 512 ГБ, Windows 11 Pro, DisplayPort, HDMI, Wi-Fi, Bluetooth, блок питания 60 Вт.", "https://www.dns-shop.ru/product/e31420e6302a6ae6/mini-pk-dexp-mini-smart-bm002/"),
        ("ПК DEXP Aquilon O310", 2, 0, 1, "Intel Pentium Gold G6405, 8 ГБ DDR4, SSD 256 ГБ, без ОС, HDMI, VGA, Intel H470, блок питания 400 Вт.", "https://www.dns-shop.ru/product/9a76eb2a9cb8d9cb/pk-dexp-aquilon-o310/"),
        ("ПК DEXP Atlas H426", 2, 0, 1, "Intel Core i3-12100, 8 ГБ DDR4, SSD 512 ГБ, без ОС, HDMI, VGA, Intel H610, блок питания 300 Вт.", "https://www.dns-shop.ru/product/d33d9335988aed20/pk-dexp-atlas-h426/"),
        ("Мини ПК DEXP Mini Smart B002", 2, 0, 1, "AMD Ryzen 7 3750H, 16 ГБ DDR4, SSD 512 ГБ, Windows 11 Pro, DisplayPort, HDMI, USB Type-C, Wi-Fi, Bluetooth, блок питания 65 Вт.", "https://www.dns-shop.ru/product/b8d806506724ed20/mini-pk-dexp-mini-smart-b002/"),
        ("ПК DEXP Mars G001", 2, 0, 1, "AMD Ryzen 5 5600G, 16 ГБ DDR4, SSD 512 ГБ, без ОС, DVI-D, HDMI, VGA, AMD B550, блок питания 500 Вт.", "https://www.dns-shop.ru/product/4778a27bc56fed20/pk-dexp-mars-g001/"),
        ("ПК DEXP Atlas H495", 2, 0, 1, "Intel Core i3-12100, 8 ГБ DDR4, SSD 256 ГБ, Windows 11 Pro, HDMI, VGA, Intel H610, блок питания 350 Вт.", "https://www.dns-shop.ru/product/5eda0e9aa6eed582/pk-dexp-atlas-h495/"),
        ("Мини ПК Inferit Mini INFR0706W", 2, 0, 1, "Intel Celeron J4125, 8 ГБ DDR4, SSD 256 ГБ, Windows 10 Pro, HDMI, VGA, блок питания 220 Вт.", "https://www.dns-shop.ru/product/5d2722dfac8bd9cb/mini-pk-inferit-mini-infr0706w/"),
        ("ПК DEXP Atlas H465", 2, 0, 1, "Intel Core i3-12100, 8 ГБ DDR4, SSD 512 ГБ, без ОС, HDMI, VGA, Intel H610, блок питания 400 Вт.", "https://www.dns-shop.ru/product/7b7437865f64d0a4/pk-dexp-atlas-h465/")
    ]
    cursor.executemany("INSERT INTO components (name, category_id, price, price_category_id, description, link) VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def delete_components_without_links():
    """Удаление компонентов без ссылок"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем все компоненты без ссылок
    cursor.execute("SELECT id FROM components WHERE link IS NULL OR link = ''")
    components_to_delete = cursor.fetchall()
    
    if not components_to_delete:
        print("Компоненты без ссылок не найдены")
        conn.close()
        return
    
    # Удаляем связи в таблице build_components
    for component in components_to_delete:
        cursor.execute("DELETE FROM build_components WHERE component_id = ?", (component[0],))
    
    # Удаляем сами компоненты
    cursor.execute("DELETE FROM components WHERE link IS NULL OR link = ''")
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"Удалено {deleted_count} компонентов без ссылок")

def bulk_add_office_builds():
    """Массовое добавление офисных бюджетных ПК в сборки (pc_builds)"""
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("Мини ПК Acer Gadget E10 ETBox [1746843]", 2, 1, 0, "Intel Core i5-12450H, 4 x 2 ГГц, 16 ГБ DDR5, SSD 512 ГБ, Windows 11 Pro, 1 x DisplayPort, 1 x HDMI, 1 x VGA (D-Sub), Wi-Fi, Bluetooth, SoC, блок питания - 120 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/1bf47191dc70d9cb/mini-pk-acer-gadget-e10-etbox-1746843/"),
        ("ПК DEXP Atlas H494", 2, 1, 0, "Intel Core i3-12100, 4 x 3.3 ГГц, 8 ГБ DDR4, SSD 256 ГБ, без ОС, 1 x HDMI, 1 x VGA (D-Sub), Intel H610, блок питания - 350 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/fb7372ffa6ecd582/pk-dexp-atlas-h494/"),
        ("Мини ПК Chuwi UBox [1746526]", 2, 1, 0, "AMD Ryzen 5 6600H, 6 x 3.3 ГГц, 16 ГБ DDR5, SSD 512 ГБ, Windows 11 Pro, 1 x DisplayPort, 1 x HDMI, Wi-Fi, Bluetooth, SoC, блок питания - 90 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/1032684d843fd582/mini-pk-chuwi-ubox-1746526/"),
        ("Мини ПК DEXP Mini Entry (8/256)", 2, 1, 0, "Intel N100, 8 ГБ DDR4, SSD 256 ГБ, Windows 11 Pro, 2 x HDMI, Wi-Fi, Bluetooth, SoC, блок питания - 36 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/80c17395c6c1eed8/mini-pk-dexp-mini-entry/"),
        ("Мини ПК DEXP Mini Entry (16/512)", 2, 1, 0, "Intel N100, 16 ГБ DDR4, SSD 512 ГБ, Windows 11 Pro, 2 x HDMI, Wi-Fi, Bluetooth, SoC, блок питания - 36 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/e10bde6713a607a3/mini-pk-dexp-mini-entry/"),
        ("Мини ПК DEXP Mini Smart BM002", 2, 1, 0, "Intel Core i5-1235U, 2 x 1.3 ГГц, 16 ГБ DDR4, SSD 512 ГБ, Windows 11 Pro, 1 x DisplayPort, 1 x HDMI, Wi-Fi, Bluetooth, SoC, блок питания - 60 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/e31420e6302a6ae6/mini-pk-dexp-mini-smart-bm002/"),
        ("ПК DEXP Aquilon O310", 2, 1, 0, "Intel Pentium Gold G6405, 2 x 4.1 ГГц, 8 ГБ DDR4, SSD 256 ГБ, без ОС, 1 x HDMI, 1 x VGA (D-Sub), Intel H470, блок питания - 400 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/9a76eb2a9cb8d9cb/pk-dexp-aquilon-o310/"),
        ("ПК DEXP Atlas H426", 2, 1, 0, "Intel Core i3-12100, 4 x 3.3 ГГц, 8 ГБ DDR4, SSD 512 ГБ, без ОС, 1 x HDMI, 1 x VGA (D-Sub), Intel H610, блок питания - 300 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/d33d9335988aed20/pk-dexp-atlas-h426/"),
        ("Мини ПК DEXP Mini Smart B002", 2, 1, 0, "AMD Ryzen 7 3750H, 4 x 2.3 ГГц, 16 ГБ DDR4, SSD 512 ГБ, Windows 11 Pro, 1 x DisplayPort, 1 x HDMI, 1 x USB Type-C, Wi-Fi, Bluetooth, SoC, блок питания - 65 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/b8d806506724ed20/mini-pk-dexp-mini-smart-b002/"),
        ("ПК DEXP Mars G001", 2, 1, 0, "AMD Ryzen 5 5600G, 6 x 3.9 ГГц, 16 ГБ DDR4, SSD 512 ГБ, без ОС, 1 x DVI-D, 1 x HDMI, 1 x VGA (D-Sub), AMD B550, блок питания - 500 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/4778a27bc56fed20/pk-dexp-mars-g001/"),
        ("ПК DEXP Atlas H495", 2, 1, 0, "Intel Core i3-12100, 4 x 3.3 ГГц, 8 ГБ DDR4, SSD 256 ГБ, Windows 11 Pro, 1 x HDMI, 1 x VGA (D-Sub), Intel H610, блок питания - 350 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/5eda0e9aa6eed582/pk-dexp-atlas-h495/"),
        ("Мини ПК Inferit Mini INFR0706W", 2, 1, 0, "Intel Celeron J4125, 4 x 2 ГГц, 8 ГБ DDR4, SSD 256 ГБ, Windows 10 Pro, 1 x HDMI, 1 x VGA (D-Sub), SoC, блок питания - 220 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/5d2722dfac8bd9cb/mini-pk-inferit-mini-infr0706w/"),
        ("ПК DEXP Atlas H465", 2, 1, 0, "Intel Core i3-12100, 4 x 3.3 ГГц, 8 ГБ DDR4, SSD 512 ГБ, без ОС, 1 x HDMI, 1 x VGA (D-Sub), Intel H610, блок питания - 400 Вт. Для уточнения цены перейдите по ссылке.", None, "https://www.dns-shop.ru/product/7b7437865f64d0a4/pk-dexp-atlas-h465/")
    ]
    cursor.executemany("""
        INSERT INTO pc_builds (name, device_type_id, price_category_id, total_price, description, image_url, link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()
    print("Офисные бюджетные ПК внесены в сборки!")

def bulk_add_storage():
    """Массовое добавление SSD и HDD накопителей в компоненты (накопители)"""
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("1000 ГБ 2.5\" SATA накопитель Samsung 870 EVO [MZ-77E1T0BW]", 4, 0, 1, "SATA, чтение - 560 Мбайт/сек, запись - 530 Мбайт/сек, 3D NAND 3 бит MLC (TLC), TBW - 600 ТБ", "https://www.dns-shop.ru/product/49172afd28f9ed20/1000-gb-25-sata-nakopitel-samsung-870-evo-mz-77e1t0bw/"),
        ("500 ГБ 2.5\" SATA накопитель Samsung 870 EVO [MZ-77E500BW]", 4, 0, 1, "SATA, чтение - 560 Мбайт/сек, запись - 530 Мбайт/сек, 3D NAND 3 бит MLC (TLC), TBW - 300 ТБ", "https://www.dns-shop.ru/product/cd3ad695f76bed20/500-gb-25-sata-nakopitel-samsung-870-evo-mz-77e500bw/"),
        ("480 ГБ 2.5\" SATA накопитель Kingston A400 [SA400S37/480G]", 4, 0, 1, "SATA, чтение - 500 Мбайт/сек, запись - 450 Мбайт/сек, 3D NAND 3 бит TLC, TBW - 160 ТБ", "https://www.dns-shop.ru/product/d74ecd0b00cded20/480-gb-25-sata-nakopitel-kingston-a400-sa400s37480g/"),
        ("960 ГБ 2.5\" SATA накопитель Kingston A400 [SA400S37/960G]", 4, 0, 1, "SATA, чтение - 500 Мбайт/сек, запись - 450 Мбайт/сек, 3D NAND 3 бит TLC, TBW - 300 ТБ", "https://www.dns-shop.ru/product/b39a8d59e7a1ed20/960-gb-25-sata-nakopitel-kingston-a400-sa400s37960g/"),
        ("4000 ГБ 2.5\" SATA накопитель Samsung 870 EVO [MZ-77E4T0BW]", 4, 0, 2, "SATA, чтение - 560 Мбайт/сек, запись - 530 Мбайт/сек, 3D NAND 3 бит MLC (TLC), TBW - 2400 ТБ", "https://www.dns-shop.ru/product/fcac32b01dd4ed20/4000-gb-25-sata-nakopitel-samsung-870-evo-mz-77e4t0bw/"),
        ("512 ГБ 2.5\" SATA накопитель Apacer AS350 PANTHER", 4, 0, 1, "SATA, чтение - 560 Мбайт/сек, запись - 540 Мбайт/сек, 3D NAND 3 бит TLC, TBW - 320 ТБ", "https://www.dns-shop.ru/product/778d8c5201153332/512-gb-25-sata-nakopitel-apacer-as350-panther/"),
        ("1000 ГБ 2.5\" SATA накопитель Apacer AS350 PANTHER [95.DB2G0.P100C]", 4, 0, 1, "SATA, чтение - 560 Мбайт/сек, запись - 540 Мбайт/сек, 3D NAND 3 бит TLC, TBW - 600 ТБ", "https://www.dns-shop.ru/product/02d939ff43d23332/1000-gb-25-sata-nakopitel-apacer-as350-panther-95db2g0p100c/"),
        ("512 ГБ 2.5\" SATA накопитель DEXP C100 [C100SMYM512]", 4, 0, 1, "SATA, чтение - 550 Мбайт/сек, запись - 495 Мбайт/сек, 3D NAND 3 бит TLC, TBW - 240 ТБ", "https://www.dns-shop.ru/product/22190260a055ed20/512-gb-25-sata-nakopitel-dexp-c100-c100smym512/"),
        ("512 ГБ 2.5\" SATA накопитель Kingston KC600 [SKC600/512G]", 4, 0, 1, "SATA, чтение - 550 Мбайт/сек, запись - 520 Мбайт/сек, 3D NAND 3 бит TLC, TBW - 300 ТБ", "https://www.dns-shop.ru/product/0e473a07e7a4ed20/512-gb-25-sata-nakopitel-kingston-kc600-skc600512g/"),
        ("1000 ГБ M.2 NVMe накопитель ADATA XPG GAMMIX S11 Pro [AGAMMIXS11P-1TT-C]", 4, 0, 2, "PCIe 3.0 x4, чтение - 3500 Мбайт/сек, запись - 3000 Мбайт/сек, 3 бит TLC, NVM Express, TBW - 640 ТБ", "https://www.dns-shop.ru/product/134e19be243b1b80/1000-gb-m2-nvme-nakopitel-adata-xpg-gammix-s11-pro-agammixs11p-1tt-c/"),
        ("1000 ГБ M.2 NVMe накопитель Samsung 990 PRO [MZ-V9P1T0BW]", 4, 0, 3, "PCIe 4.0 x4, чтение - 7450 Мбайт/сек, запись - 6900 Мбайт/сек, 3 бит MLC (TLC), NVM Express, TBW - 600 ТБ", "https://www.dns-shop.ru/product/39779619c38e0fd2/1000-gb-m2-nvme-nakopitel-samsung-990-pro-mz-v9p1t0bw/"),
        ("2000 ГБ M.2 NVMe накопитель Kingston FURY Renegade [SFYRD/2000G]", 4, 0, 3, "PCIe 4.0 x4, чтение - 7300 Мбайт/сек, запись - 7000 Мбайт/сек, 3 бит TLC, NVM Express, TBW - 2000 ТБ", "https://www.dns-shop.ru/product/00e0e2b0e7a2ed20/2000-gb-m2-nvme-nakopitel-kingston-fury-renegade-sfyrd2000g/"),
        ("1000 ГБ M.2 NVMe накопитель ADATA LEGEND 960 MAX [ALEG-960M-1TCS]", 4, 0, 3, "PCIe 4.0 x4, чтение - 7400 Мбайт/сек, запись - 6000 Мбайт/сек, NVM Express, TBW - 780 ТБ", "https://www.dns-shop.ru/product/c413c3309562ed20/1000-gb-m2-nvme-nakopitel-adata-legend-960-max-aleg-960m-1tcs/"),
        ("2000 ГБ M.2 NVMe накопитель Kingston KC3000 [SKC3000D/2048G]", 4, 0, 3, "PCIe 4.0 x4, чтение - 7000 Мбайт/сек, запись - 7000 Мбайт/сек, 3 бит TLC, NVM Express, TBW - 1600 ТБ", "https://www.dns-shop.ru/product/f6e523df00d4ed20/2000-gb-m2-nvme-nakopitel-kingston-kc3000-skc3000d2048g/"),
        ("1000 ГБ M.2 NVMe накопитель Samsung 980 [MZ-V8V1T0BW]", 4, 0, 2, "PCIe 3.0 x4, чтение - 3500 Мбайт/сек, запись - 3000 Мбайт/сек, 3 бит MLC (TLC), NVM Express, TBW - 600 ТБ", "https://www.dns-shop.ru/product/2f1ccf93dc09ed20/1000-gb-m2-nvme-nakopitel-samsung-980-mz-v8v1t0bw/"),
        ("1024 ГБ M.2 NVMe накопитель ARDOR GAMING Ally AL1288 [ALMAYM1024-AL1288]", 4, 0, 2, "PCIe 3.0 x4, чтение - 3300 Мбайт/сек, запись - 3100 Мбайт/сек, 3 бит TLC, NVM Express, TBW - 750 ТБ", "https://www.dns-shop.ru/product/d52e61cac251ed20/1024-gb-m2-nvme-nakopitel-ardor-gaming-ally-al1288-almaym1024-al1288/"),
        ("4 ТБ Жесткий диск WD Purple Surveillance [WD43PURZ]", 4, 0, 2, "SATA III, 6 Гбит/с, 5400 об/мин, кэш память - 256 МБ, RAID Edition", "https://www.dns-shop.ru/product/3d4515c1e40aed20/4-tb-zestkij-disk-wd-purple-surveillance-wd43purz/"),
        ("1 ТБ Жесткий диск WD Blue [WD10EZEX]", 4, 0, 1, "SATA III, 6 Гбит/с, 7200 об/мин, кэш память - 64 МБ", "https://www.dns-shop.ru/product/c9fb736ee65bed20/1-tb-zestkij-disk-wd-blue-wd10ezex/"),
        ("8 ТБ Жесткий диск WD Purple [WD85PURZ]", 4, 0, 3, "SATA III, 6 Гбит/с, 5640 об/мин, кэш память - 256 МБ", "https://www.dns-shop.ru/product/c57e6520220dd9cb/8-tb-zestkij-disk-wd-purple-wd85purz/"),
        ("4 ТБ Жесткий диск WD Red Plus [WD40EFPX]", 4, 0, 2, "SATA III, 6 Гбит/с, 5400 об/мин, кэш память - 256 МБ, RAID Edition", "https://www.dns-shop.ru/product/2bde2b185db3ed20/4-tb-zestkij-disk-wd-red-plus-wd40efpx/"),
        ("8 ТБ Жесткий диск Seagate SkyHawk [ST8000VX010]", 4, 0, 3, "SATA III, 6 Гбит/с, кэш память - 256 МБ, RAID Edition", "https://www.dns-shop.ru/product/3c44a7bee4d7ed20/8-tb-zestkij-disk-seagate-skyhawk-st8000vx010/"),
        ("2 ТБ Жесткий диск WD Red Plus [WD20EFPX]", 4, 0, 2, "SATA III, 6 Гбит/с, 5400 об/мин, кэш память - 64 МБ, RAID Edition", "https://www.dns-shop.ru/product/738f45d55dc0ed20/2-tb-zestkij-disk-wd-red-plus-wd20efpx/")
    ]
    cursor.executemany("""
        INSERT INTO components (name, category_id, price, price_category_id, description, link)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()
    print("SSD и HDD накопители внесены в компоненты!")

def bulk_add_gpus_extra():
    """Массовое добавление новых видеокарт в компоненты (видеокарты)"""
    import sqlite3
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    data = [
        ("Видеокарта PNY Quadro RTX 5000 Ada Generation", 2, 0, 3, "PCIe 4.0 32 ГБ GDDR6, 256 бит, 4 x DisplayPort, GPU 1155 МГц", "https://www.dns-shop.ru/product/47e1086174aed9cb/videokarta-pny-quadro-rtx-5000-ada-generation-vcnrtx5000ada-sb/"),
        ("Видеокарта ASUS GeForce RTX 5090 ROG Astral OC Edition", 2, 0, 3, "PCIe 5.0 32 ГБ GDDR7, 512 бит, 2 x HDMI, 3 x DisplayPort, GPU 2017 МГц", "https://www.dns-shop.ru/product/ad7f908a0dd6d582/videokarta-asus-geforce-rtx-5090-rog-astral-oc-edition-rog-astral-rtx5090-o32g-gaming/"),
        ("Видеокарта DEXP GeForce 210", 2, 0, 1, "PCIe 2.0 1 ГБ DDR3, 64 бит, DVI-I, HDMI, VGA (D-Sub), GPU 500 МГц", "https://www.dns-shop.ru/product/6eb69e7b500fd309/videokarta-dexp-geforce-210-gt210-1gd3-lp/"),
        ("Видеокарта DEXP GeForce GT 730", 2, 0, 1, "PCIe 2.0 4 ГБ DDR3, 128 бит, DVI-D, HDMI, VGA (D-Sub), GPU 700 МГц", "https://www.dns-shop.ru/product/eee71bbc95752a9a/videokarta-dexp-geforce-gt-730-gt730-4gd3-lp/"),
        ("Видеокарта PowerColor AMD Radeon 550", 2, 0, 1, "PCIe 3.0 2 ГБ GDDR5, 64 бит, DVI-D, HDMI, GPU 1100 МГц", "https://www.dns-shop.ru/product/48f5e3b94dc6ed20/videokarta-powercolor-amd-radeon-550-axrx-550-2gbd5-hlev2/"),
        ("Видеокарта DEXP GeForce GT 1030", 2, 0, 1, "PCIe 3.0 2 ГБ GDDR5, 64 бит, DVI-D, HDMI, GPU 1228 МГц", "https://www.dns-shop.ru/product/d1b49777244b06d3/videokarta-dexp-geforce-gt-1030-gt1030-2gd5-lp/"),
        ("Видеокарта Sapphire AMD Radeon RX 6400 PULSE", 2, 0, 2, "PCIe 4.0 4 ГБ GDDR6, 64 бит, DisplayPort, HDMI, GPU 1923 МГц", "https://www.dns-shop.ru/product/ed507639d4d9ed20/videokarta-sapphire-amd-radeon-rx-6400-pulse-11315-01-20g/"),
        ("Видеокарта PNY Quadro T400", 2, 0, 1, "PCIe 3.0 4 ГБ GDDR6, 64 бит, 3 x Mini DisplayPort, GPU 1070 МГц", "https://www.dns-shop.ru/product/9c3c2d9eeb9eed20/videokarta-pny-quadro-t400-vcnt400-4gb-sb/"),
        ("Видеокарта GIGABYTE Intel Arc A380 GAMING OC", 2, 0, 2, "PCIe 4.0 6 ГБ GDDR6, 96 бит, 2 x DisplayPort, 2 x HDMI, GPU 2000 МГц", "https://www.dns-shop.ru/product/e87ba8ad4a09ed20/videokarta-gigabyte-intel-arc-a380-gaming-oc-gv-ia380gaming-oc-6gd/"),
        ("Видеокарта ASRock AMD Radeon RX 6600 Challenger D", 2, 0, 2, "PCIe 4.0 8 ГБ GDDR6, 128 бит, 3 x DisplayPort, HDMI, GPU 1626 МГц", "https://www.dns-shop.ru/product/4bb4202e5d77ed20/videokarta-asrock-amd-radeon-rx-6600-challenger-d-rx6600-cld-8g/"),
        ("Видеокарта ASRock Intel Arc A580 Challenger OC", 2, 0, 2, "PCIe 4.0 8 ГБ GDDR6, 256 бит, 3 x DisplayPort, HDMI, GPU 1700 МГц", "https://www.dns-shop.ru/product/b4df3eca7e2fed20/videokarta-asrock-intel-arc-a580-challenger-oc-a580-cl-8go/"),
        ("Видеокарта GIGABYTE Intel Arc A310 WINDFORCE", 2, 0, 1, "PCIe 4.0 4 ГБ GDDR6, 64 бит, 2 x DisplayPort, 2 x HDMI, GPU 2000 МГц", "https://www.dns-shop.ru/product/2acf3ace4ab7ed20/videokarta-gigabyte-intel-arc-a310-windforce-gv-ia310wf2-4gd/")
    ]
    cursor.executemany("""
        INSERT INTO components (name, category_id, price, price_category_id, description, link)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()
    print("Дополнительные видеокарты внесены в компоненты!")

# Инициализация БД при импорте модуля
init_db()