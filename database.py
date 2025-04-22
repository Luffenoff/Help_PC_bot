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
    
    # Проверяем, нужно ли заполнить типы устройств
    cursor.execute("SELECT COUNT(*) FROM device_types")
    if cursor.fetchone()[0] == 0:
        device_types = [
            (1, "Игровой ПК", "Компьютеры для игр с высокой производительностью"),
            (2, "Рабочий ПК", "Компьютеры для работы и офисного использования"),
            (3, "Ноутбук", "Портативные компьютеры для мобильного использования")
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
    print(f"База данных инициализирована: {DATABASE_FILE}")

# Функции для работы с базой данных

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

def get_random_build(price_category_id: int) -> dict:
    """Получает случайную сборку для указанной ценовой категории"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем все сборки для указанной ценовой категории
    cursor.execute("""
        SELECT id, name, price, description, link
        FROM pc_builds
        WHERE price_category_id = ?
    """, (price_category_id,))
    
    builds = cursor.fetchall()
    conn.close()
    
    if not builds:
        return None
    
    # Выбираем случайную сборку
    build = random.choice(builds)
    
    # Преобразуем в словарь
    return {
        'id': build[0],
        'name': build[1],
        'price': build[2],
        'description': build[3],
        'link': build[4]
    }

def add_your_builds():
    """Добавление ваших сборок в базу данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ваши сборки
    your_builds = [
        # Формат: (id, name, device_type_id, price_category_id, total_price, description, image_url, link)
        # device_type_id: 1 - игровой ПК, 2 - рабочий ПК, 3 - ноутбук
        # price_category_id: 1 - бюджетный, 2 - средний, 3 - премиум
        
        # Игровые ПК
        (10, "Игровой ПК Бюджет", 1, 1, 35000, 
         "Бюджетный игровой ПК для начинающих геймеров", 
         None, 
         "https://example.com/your_build1"),
         
        (11, "Игровой ПК Средний", 1, 2, 60000, 
         "Сбалансированный игровой ПК для комфортного гейминга", 
         None, 
         "https://example.com/your_build2"),
         
        (12, "Игровой ПК Премиум", 1, 3, 120000, 
         "Мощный игровой ПК для профессиональных геймеров", 
         None, 
         "https://example.com/your_build3"),
        
        # Рабочие ПК
        (13, "Рабочий ПК Бюджет", 2, 1, 30000, 
         "Бюджетный ПК для офисных задач", 
         None, 
         "https://example.com/your_build4"),
         
        (14, "Рабочий ПК Средний", 2, 2, 50000, 
         "Сбалансированный ПК для работы с графикой", 
         None, 
         "https://example.com/your_build5"),
         
        (15, "Рабочий ПК Премиум", 2, 3, 100000, 
         "Мощный ПК для профессиональной работы", 
         None, 
         "https://example.com/your_build6"),
        
        # Ноутбуки
        (16, "Ноутбук Бюджет", 3, 1, 40000, 
         "Бюджетный ноутбук для повседневных задач", 
         None, 
         "https://example.com/your_build7"),
         
        (17, "Ноутбук Средний", 3, 2, 70000, 
         "Сбалансированный ноутбук для работы и развлечений", 
         None, 
         "https://example.com/your_build8"),
         
        (18, "Ноутбук Премиум", 3, 3, 150000, 
         "Мощный ноутбук для профессионального использования", 
         None, 
         "https://example.com/your_build9")
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO pc_builds 
        (id, name, device_type_id, price_category_id, total_price, description, image_url, link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, your_builds)
    
    conn.commit()
    conn.close()
    print("Ваши сборки добавлены в базу данных")

# Инициализация БД при импорте модуля
init_db()