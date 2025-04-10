import sqlite3
import json
from datetime import datetime

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

def add_build(name, device_type_id, price_category_id, description="", component_ids=None, image_url=None):
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

def add_test_data():
    """Добавление тестовых данных в базу для демонстрации"""
    # Добавляем компоненты
    cpu_budget = add_component(
        name="Intel Core i3-12100F",
        category_id=1,  # Процессоры
        price=7990,
        price_category_id=1,  # Бюджетный
        description="4-ядерный процессор начального уровня 12-го поколения",
        specs={
            "Ядра": "4",
            "Потоки": "8",
            "Базовая частота": "3.3 GHz",
            "Турбо частота": "4.3 GHz",
            "TDP": "65W"
        }
    )
    
    cpu_mid = add_component(
        name="AMD Ryzen 5 5600X",
        category_id=1,  # Процессоры
        price=16990,
        price_category_id=2,  # Средний
        description="6-ядерный процессор среднего уровня с высокой производительностью",
        specs={
            "Ядра": "6",
            "Потоки": "12",
            "Базовая частота": "3.7 GHz",
            "Турбо частота": "4.6 GHz",
            "TDP": "65W"
        }
    )
    
    cpu_premium = add_component(
        name="Intel Core i7-13700K",
        category_id=1,  # Процессоры
        price=39990,
        price_category_id=3,  # Премиум
        description="16-ядерный процессор высокого уровня 13-го поколения",
        specs={
            "Ядра": "16 (8P+8E)",
            "Потоки": "24",
            "Базовая частота": "3.4 GHz",
            "Турбо частота": "5.4 GHz",
            "TDP": "125W"
        }
    )
    
    gpu_budget = add_component(
        name="NVIDIA GeForce GTX 1650",
        category_id=2,  # Видеокарты
        price=15990,
        price_category_id=1,  # Бюджетный
        description="Видеокарта начального уровня для игр с низкими/средними настройками",
        specs={
            "Память": "4 GB GDDR6",
            "Частота памяти": "8 Gbps",
            "Шина памяти": "128-bit",
            "TDP": "75W"
        }
    )
    
    gpu_mid = add_component(
        name="NVIDIA GeForce RTX 3060",
        category_id=2,  # Видеокарты
        price=32990,
        price_category_id=2,  # Средний
        description="Видеокарта среднего уровня с поддержкой трассировки лучей",
        specs={
            "Память": "12 GB GDDR6",
            "Частота памяти": "15 Gbps",
            "Шина памяти": "192-bit",
            "TDP": "170W"
        }
    )
    
    gpu_premium = add_component(
        name="NVIDIA GeForce RTX 4080",
        category_id=2,  # Видеокарты
        price=109990,
        price_category_id=3,  # Премиум
        description="Высокопроизводительная видеокарта нового поколения Ada Lovelace",
        specs={
            "Память": "16 GB GDDR6X",
            "Частота памяти": "22.4 Gbps",
            "Шина памяти": "256-bit",
            "TDP": "320W"
        }
    )
    
    ram_budget = add_component(
        name="Crucial 16GB DDR4 3200MHz",
        category_id=3,  # Оперативная память
        price=4990,
        price_category_id=1,  # Бюджетный
        description="Комплект памяти 2x8GB для базовых систем",
        specs={
            "Объем": "16GB (2x8GB)",
            "Тип": "DDR4",
            "Частота": "3200 MHz",
            "Тайминги": "CL16"
        }
    )
    
    ram_mid = add_component(
        name="Kingston FURY Beast 32GB DDR4 3600MHz",
        category_id=3,  # Оперативная память
        price=11990,
        price_category_id=2,  # Средний
        description="Производительная память с подсветкой RGB",
        specs={
            "Объем": "32GB (2x16GB)",
            "Тип": "DDR4",
            "Частота": "3600 MHz",
            "Тайминги": "CL18"
        }
    )
    
    ram_premium = add_component(
        name="G.Skill Trident Z5 RGB 64GB DDR5 6000MHz",
        category_id=3,  # Оперативная память
        price=29990,
        price_category_id=3,  # Премиум
        description="Высокоскоростная память DDR5 с RGB подсветкой",
        specs={
            "Объем": "64GB (2x32GB)",
            "Тип": "DDR5",
            "Частота": "6000 MHz",
            "Тайминги": "CL36"
        }
    )
    
    storage_budget = add_component(
        name="Samsung 980 500GB NVMe SSD",
        category_id=4,  # Накопители
        price=4990,
        price_category_id=1,  # Бюджетный
        description="Быстрый SSD накопитель для базовых задач",
        specs={
            "Объем": "500GB",
            "Интерфейс": "PCIe 3.0 x4 NVMe",
            "Скорость чтения": "3500 MB/s",
            "Скорость записи": "2900 MB/s"
        }
    )
    
    storage_mid = add_component(
        name="Samsung 970 EVO Plus 1TB NVMe SSD",
        category_id=4,  # Накопители
        price=10990,
        price_category_id=2,  # Средний
        description="Производительный NVMe SSD накопитель",
        specs={
            "Объем": "1TB",
            "Интерфейс": "PCIe 3.0 x4 NVMe",
            "Скорость чтения": "3500 MB/s",
            "Скорость записи": "3300 MB/s"
        }
    )
    
    storage_premium = add_component(
        name="Samsung 990 PRO 2TB NVMe SSD",
        category_id=4,  # Накопители
        price=24990,
        price_category_id=3,  # Премиум
        description="Высокопроизводительный NVMe SSD накопитель PCIe 4.0",
        specs={
            "Объем": "2TB",
            "Интерфейс": "PCIe 4.0 x4 NVMe",
            "Скорость чтения": "7450 MB/s",
            "Скорость записи": "6900 MB/s"
        }
    )
    
    # Добавляем сборки PC
    gaming_pc_budget = add_build(
        name="Игровой ПК Старт",
        device_type_id=1,  # Игровой ПК
        price_category_id=1,  # Бюджетный
        description="Базовая игровая сборка для несложных игр и киберспортивных дисциплин",
        component_ids=[cpu_budget, gpu_budget, ram_budget, storage_budget]
    )
    
    gaming_pc_mid = add_build(
        name="Игровой ПК Баланс",
        device_type_id=1,  # Игровой ПК
        price_category_id=2,  # Средний
        description="Оптимальная игровая сборка для современных игр в Full HD разрешении",
        component_ids=[cpu_mid, gpu_mid, ram_mid, storage_mid]
    )
    
    gaming_pc_premium = add_build(
        name="Игровой ПК Ультра",
        device_type_id=1,  # Игровой ПК
        price_category_id=3,  # Премиум
        description="Мощная игровая сборка для 4K-гейминга и стриминга",
        component_ids=[cpu_premium, gpu_premium, ram_premium, storage_premium]
    )
    
    work_pc_budget = add_build(
        name="Рабочий ПК Офис",
        device_type_id=2,  # Рабочий ПК
        price_category_id=1,  # Бюджетный
        description="Базовая сборка для офисных задач и интернета",
        component_ids=[cpu_budget, ram_budget, storage_budget]
    )
    
    work_pc_mid = add_build(
        name="Рабочий ПК Профи",
        device_type_id=2,  # Рабочий ПК
        price_category_id=2,  # Средний
        description="Оптимальная сборка для работы с графикой и видеомонтажа",
        component_ids=[cpu_mid, gpu_mid, ram_mid, storage_mid]
    )
    
    work_pc_premium = add_build(
        name="Рабочий ПК Студия",
        device_type_id=2,  # Рабочий ПК
        price_category_id=3,  # Премиум
        description="Высокопроизводительная рабочая станция для 3D-рендеринга и сложных вычислений",
        component_ids=[cpu_premium, gpu_premium, ram_premium, storage_premium]
    )
    
    print("Тестовые данные успешно добавлены в базу")

# Инициализация БД при импорте модуля
init_db()