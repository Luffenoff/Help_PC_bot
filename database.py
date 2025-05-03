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

def get_random_build() -> dict:
    """Получение случайной сборки со всеми компонентами"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем случайную сборку
    cursor.execute("""
        SELECT id, name, device_type_id, price_category_id, total_price, description, link
        FROM pc_builds
        ORDER BY RANDOM()
        LIMIT 1
    """)
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

def add_dns_build():
    """Добавление сборки из DNS"""
    # Сначала добавляем компоненты
    components = [
        {
            'name': 'Intel Core i5-12400F OEM',
            'category_id': 1,  # Процессоры
            'price': 9899,
            'price_category_id': 2,  # Средний
            'description': 'Процессор Intel Core i5-12400F OEM [LGA 1700, 6 x 2.5 ГГц, L2 - 7.5 МБ, L3 - 18 МБ, 2 х DDR4, DDR5-4800 МГц, TDP 117 Вт]',
            'specs': {
                'socket': 'LGA 1700',
                'cores': 6,
                'threads': 12,
                'base_clock': '2.5 ГГц',
                'l2_cache': '7.5 МБ',
                'l3_cache': '18 МБ',
                'memory_type': 'DDR4, DDR5-4800 МГц',
                'tdp': '117 Вт'
            }
        },
        {
            'name': 'GIGABYTE B760M DS3H DDR4',
            'category_id': 5,  # Материнские платы
            'price': 8499,
            'price_category_id': 2,  # Средний
            'description': 'Материнская плата GIGABYTE B760M DS3H DDR4 [LGA 1700, Intel B760, 4xDDR4-3200 МГц, 1xPCI-Ex16, 2xM.2, Micro-ATX]',
            'specs': {
                'socket': 'LGA 1700',
                'chipset': 'Intel B760',
                'memory_slots': 4,
                'memory_type': 'DDR4-3200 МГц',
                'pcie_slots': '1xPCI-Ex16',
                'm2_slots': 2,
                'form_factor': 'Micro-ATX'
            }
        },
        {
            'name': 'KFA2 GeForce RTX 4060 CORE Black',
            'category_id': 2,  # Видеокарты
            'price': 31999,
            'price_category_id': 2,  # Средний
            'description': 'Видеокарта KFA2 GeForce RTX 4060 CORE Black [PCIe 4.0 8 ГБ GDDR6, 128 бит, 3 x DisplayPort, HDMI, GPU 1830 МГц]',
            'specs': {
                'memory': '8 ГБ GDDR6',
                'memory_bus': '128 бит',
                'ports': '3 x DisplayPort, HDMI',
                'gpu_clock': '1830 МГц',
                'interface': 'PCIe 4.0'
            }
        },
        {
            'name': 'Kingston FURY Beast Black 32 ГБ',
            'category_id': 3,  # Оперативная память
            'price': 6899,
            'price_category_id': 2,  # Средний
            'description': 'Оперативная память Kingston FURY Beast Black [KF432C16BBK2/32] 32 ГБ [DDR4, 16 ГБx2 шт, 3200 МГц, 16(CL)-20-20]',
            'specs': {
                'capacity': '32 ГБ',
                'modules': '16 ГБx2 шт',
                'type': 'DDR4',
                'speed': '3200 МГц',
                'timings': '16(CL)-20-20'
            }
        },
        {
            'name': 'ADATA XPG GAMMIX S11 Pro 1TB',
            'category_id': 4,  # Накопители
            'price': 5799,
            'price_category_id': 2,  # Средний
            'description': '1000 ГБ M.2 NVMe накопитель ADATA XPG GAMMIX S11 Pro [PCIe 3.0 x4, чтение - 3500 Мбайт/сек, запись - 3000 Мбайт/сек, 3 бит TLC, NVM Express, TBW - 640 ТБ]',
            'specs': {
                'capacity': '1000 ГБ',
                'interface': 'PCIe 3.0 x4',
                'read_speed': '3500 Мбайт/сек',
                'write_speed': '3000 Мбайт/сек',
                'type': '3 бит TLC',
                'tbw': '640 ТБ'
            }
        },
        {
            'name': 'DEEPCOOL PF750',
            'category_id': 6,  # Блоки питания
            'price': 4999,
            'price_category_id': 2,  # Средний
            'description': 'Блок питания DEEPCOOL PF750 [R-PF750D-HA0B-EU] черный [750 Вт, 80+, APFC, 20+4 pin, 2 x 4+4 pin CPU, 6 SATA, 4 x 6+2 pin PCI-E]',
            'specs': {
                'power': '750 Вт',
                'efficiency': '80+',
                'features': 'APFC',
                'connectors': '20+4 pin, 2 x 4+4 pin CPU, 6 SATA, 4 x 6+2 pin PCI-E'
            }
        },
        {
            'name': 'Cougar FV150 RGB',
            'category_id': 8,  # Корпуса
            'price': 7999,
            'price_category_id': 2,  # Средний
            'description': 'Корпус Cougar FV150 RGB [FV150 RGB black] черный [Mid-Tower, Micro-ATX, Mini-ITX, Standard-ATX, USB 3.2 Gen 1 Type-A, USB 3.2 Gen 2 Type-C, ARGB вентиляторы, 4 x 120 мм]',
            'specs': {
                'form_factor': 'Mid-Tower',
                'supported_motherboards': 'Micro-ATX, Mini-ITX, Standard-ATX',
                'usb_ports': 'USB 3.2 Gen 1 Type-A, USB 3.2 Gen 2 Type-C',
                'fans': 'ARGB вентиляторы, 4 x 120 мм'
            }
        },
        {
            'name': 'DEEPCOOL AG300 MARRS',
            'category_id': 7,  # Охлаждение
            'price': 1250,
            'price_category_id': 2,  # Средний
            'description': 'Кулер для процессора DEEPCOOL AG300 MARRS [R-AG300-BKMNMN-G] [основание - алюминий\медь, 3050 об/мин, 30.5 дБ, 4 pin, 150 Вт]',
            'specs': {
                'base_material': 'алюминий\медь',
                'fan_speed': '3050 об/мин',
                'noise_level': '30.5 дБ',
                'connector': '4 pin',
                'tdp': '150 Вт'
            }
        }
    ]
    
    # Добавляем компоненты
    component_ids = []
    for component in components:
        specs_json = json.dumps(component.get('specs')) if component.get('specs') else None
        component_id = add_component(
            name=component['name'],
            category_id=component['category_id'],
            price=component['price'],
            price_category_id=component['price_category_id'],
            description=component['description'],
            specs=specs_json
        )
        component_ids.append(component_id)
    
    # Создаем сборку
    return add_build(
        name='Игровой ПК DNS (i5-12400F + RTX 4060)',
        device_type_id=1,  # Игровой ПК
        price_category_id=2,  # Средний
        description='Сбалансированный игровой ПК на базе процессора Intel Core i5-12400F и видеокарты RTX 4060. Отличный выбор для современных игр в разрешении 1080p.',
        link='https://www.dns-shop.ru/configurator/',
        component_ids=component_ids
    )

def add_dns_build_2():
    """Добавление новой сборки из DNS"""
    # Сначала добавляем компоненты
    components = [
        {
            'name': 'Intel Core i5-13400F OEM',
            'category_id': 1,  # Процессоры
            'price': 11399,
            'price_category_id': 2,  # Средний
            'description': 'Процессор Intel Core i5-13400F OEM [LGA 1700, 6P x 2.5 ГГц, 4E x 1.8 ГГц, L2 - 9.5 МБ, L3 - 20 МБ, 2 х DDR4, DDR5-4800 МГц, TDP 148 Вт]',
            'specs': {
                'socket': 'LGA 1700',
                'p_cores': 6,
                'e_cores': 4,
                'p_clock': '2.5 ГГц',
                'e_clock': '1.8 ГГц',
                'l2_cache': '9.5 МБ',
                'l3_cache': '20 МБ',
                'memory_type': 'DDR4, DDR5-4800 МГц',
                'tdp': '148 Вт'
            }
        },
        {
            'name': 'MSI B760 GAMING PLUS WIFI',
            'category_id': 5,  # Материнские платы
            'price': 13299,
            'price_category_id': 2,  # Средний
            'description': 'Материнская плата MSI B760 GAMING PLUS WIFI [LGA 1700, Intel B760, 4xDDR5-5600 МГц, 5xPCI-Ex16, 2xM.2, Standard-ATX]',
            'specs': {
                'socket': 'LGA 1700',
                'chipset': 'Intel B760',
                'memory_slots': 4,
                'memory_type': 'DDR5-5600 МГц',
                'pcie_slots': '5xPCI-Ex16',
                'm2_slots': 2,
                'form_factor': 'Standard-ATX',
                'wifi': True
            }
        },
        {
            'name': 'MSI GeForce RTX 4060 VENTUS 2X WHITE OC',
            'category_id': 2,  # Видеокарты
            'price': 33999,
            'price_category_id': 2,  # Средний
            'description': 'Видеокарта MSI GeForce RTX 4060 VENTUS 2X WHITE OC [PCIe 4.0 8 ГБ GDDR6, 128 бит, 3 x DisplayPort, HDMI, GPU 1830 МГц]',
            'specs': {
                'memory': '8 ГБ GDDR6',
                'memory_bus': '128 бит',
                'ports': '3 x DisplayPort, HDMI',
                'gpu_clock': '1830 МГц',
                'interface': 'PCIe 4.0'
            }
        },
        {
            'name': 'ADATA XPG Lancer Blade RGB 32 ГБ',
            'category_id': 3,  # Оперативная память
            'price': 10499,
            'price_category_id': 2,  # Средний
            'description': 'Оперативная память ADATA XPG Lancer Blade RGB [AX5U6000C3016G-DTLABRBK] 32 ГБ [DDR5, 16 ГБx2 шт, 6000 МГц, 30(CL)-40-40]',
            'specs': {
                'capacity': '32 ГБ',
                'modules': '16 ГБx2 шт',
                'type': 'DDR5',
                'speed': '6000 МГц',
                'timings': '30(CL)-40-40',
                'rgb': True
            }
        },
        {
            'name': 'ADATA LEGEND 960 MAX 1TB',
            'category_id': 4,  # Накопители
            'price': 8799,
            'price_category_id': 2,  # Средний
            'description': '1000 ГБ M.2 NVMe накопитель ADATA LEGEND 960 MAX [ALEG-960M-1TCS] [PCIe 4.0 x4, чтение - 7400 Мбайт/сек, запись - 6000 Мбайт/сек, NVM Express, TBW - 780 ТБ]',
            'specs': {
                'capacity': '1000 ГБ',
                'interface': 'PCIe 4.0 x4',
                'read_speed': '7400 Мбайт/сек',
                'write_speed': '6000 Мбайт/сек',
                'type': 'NVM Express',
                'tbw': '780 ТБ'
            }
        },
        {
            'name': 'Cougar STX 700W',
            'category_id': 6,  # Блоки питания
            'price': 4499,
            'price_category_id': 2,  # Средний
            'description': 'Блок питания Cougar STX 700W [CGR ST-700] черный [700 Вт, 80+, APFC, 20+4 pin, 4+4 pin, 8 pin CPU, 6 SATA, 2 x 6+2 pin PCI-E]',
            'specs': {
                'power': '700 Вт',
                'efficiency': '80+',
                'features': 'APFC',
                'connectors': '20+4 pin, 4+4 pin, 8 pin CPU, 6 SATA, 2 x 6+2 pin PCI-E'
            }
        },
        {
            'name': 'Cougar Duoface Pro RGB White',
            'category_id': 8,  # Корпуса
            'price': 8599,
            'price_category_id': 2,  # Средний
            'description': 'Корпус Cougar Duoface Pro RGB White белый [Mid-Tower, E-ATX, Micro-ATX, Mini-ITX, SSI-CEB, USB 2.0 Type-A, USB 3.2 Gen 1 Type-A, USB 3.2 Gen 1 Type-C, ARGB вентиляторы, 4 x 120 мм]',
            'specs': {
                'form_factor': 'Mid-Tower',
                'supported_motherboards': 'E-ATX, Micro-ATX, Mini-ITX, SSI-CEB',
                'usb_ports': 'USB 2.0 Type-A, USB 3.2 Gen 1 Type-A, USB 3.2 Gen 1 Type-C',
                'fans': 'ARGB вентиляторы, 4 x 120 мм'
            }
        },
        {
            'name': 'DEEPCOOL AK400 WH',
            'category_id': 7,  # Охлаждение
            'price': 2699,
            'price_category_id': 2,  # Средний
            'description': 'Кулер для процессора DEEPCOOL AK400 WH [R-AK400-WHNNMN-G-1] [основание - алюминий\медь, 1850 об/мин, 29 дБ, 4 pin, 220 Вт]',
            'specs': {
                'base_material': 'алюминий\медь',
                'fan_speed': '1850 об/мин',
                'noise_level': '29 дБ',
                'connector': '4 pin',
                'tdp': '220 Вт'
            }
        }
    ]
    
    # Добавляем компоненты
    component_ids = []
    for component in components:
        specs_json = json.dumps(component.get('specs')) if component.get('specs') else None
        component_id = add_component(
            name=component['name'],
            category_id=component['category_id'],
            price=component['price'],
            price_category_id=component['price_category_id'],
            description=component['description'],
            specs=specs_json
        )
        component_ids.append(component_id)
    
    # Создаем сборку
    return add_build(
        name='Игровой ПК DNS (i5-13400F + RTX 4060)',
        device_type_id=1,  # Игровой ПК
        price_category_id=2,  # Средний
        description='Мощный игровой ПК на базе процессора Intel Core i5-13400F и видеокарты RTX 4060. Отличный выбор для современных игр в разрешении 1080p и 1440p.',
        link='https://www.dns-shop.ru/user-pc/configuration/1aa529f5cd09801a/',
        component_ids=component_ids
    )

def add_dns_build_3():
    """Добавление новой сборки из DNS с процессором AMD"""
    # Сначала добавляем компоненты
    components = [
        {
            'name': 'AMD Ryzen 5 7500F OEM',
            'category_id': 1,  # Процессоры
            'price': 14299,
            'price_category_id': 3,  # Премиум
            'description': 'Процессор AMD Ryzen 5 7500F OEM [AM5, 6 x 3.7 ГГц, L2 - 6 МБ, L3 - 32 МБ, 2 х DDR5-5200 МГц, TDP 65 Вт]',
            'specs': {
                'socket': 'AM5',
                'cores': 6,
                'clock': '3.7 ГГц',
                'l2_cache': '6 МБ',
                'l3_cache': '32 МБ',
                'memory_type': 'DDR5-5200 МГц',
                'tdp': '65 Вт'
            }
        },
        {
            'name': 'MSI B650M GAMING PLUS WIFI',
            'category_id': 5,  # Материнские платы
            'price': 15999,
            'price_category_id': 3,  # Премиум
            'description': 'Материнская плата MSI B650M GAMING PLUS WIFI [AM5, AMD B650, 4xDDR5-4800 МГц, 1xPCI-Ex16, 2xM.2, Micro-ATX]',
            'specs': {
                'socket': 'AM5',
                'chipset': 'AMD B650',
                'memory_slots': 4,
                'memory_type': 'DDR5-4800 МГц',
                'pcie_slots': '1xPCI-Ex16',
                'm2_slots': 2,
                'form_factor': 'Micro-ATX',
                'wifi': True
            }
        },
        {
            'name': 'Palit GeForce RTX 5070 Ti GamingPro',
            'category_id': 2,  # Видеокарты
            'price': 96999,
            'price_category_id': 3,  # Премиум
            'description': 'Видеокарта Palit GeForce RTX 5070 Ti GamingPro [PCIe 5.0 16 ГБ GDDR7, 256 бит, 3 x DisplayPort, HDMI, GPU 2295 МГц]',
            'specs': {
                'memory': '16 ГБ GDDR7',
                'memory_bus': '256 бит',
                'ports': '3 x DisplayPort, HDMI',
                'gpu_clock': '2295 МГц',
                'interface': 'PCIe 5.0'
            }
        },
        {
            'name': 'ADATA XPG Lancer Blade RGB 32 ГБ',
            'category_id': 3,  # Оперативная память
            'price': 10499,
            'price_category_id': 3,  # Премиум
            'description': 'Оперативная память ADATA XPG Lancer Blade RGB [AX5U6000C3016G-DTLABRBK] 32 ГБ [DDR5, 16 ГБx2 шт, 6000 МГц, 30(CL)-40-40]',
            'specs': {
                'capacity': '32 ГБ',
                'modules': '16 ГБx2 шт',
                'type': 'DDR5',
                'speed': '6000 МГц',
                'timings': '30(CL)-40-40',
                'rgb': True
            }
        },
        {
            'name': 'Kingston NV2 1TB',
            'category_id': 4,  # Накопители
            'price': 6799,
            'price_category_id': 3,  # Премиум
            'description': '1000 ГБ M.2 NVMe накопитель Kingston NV2 [SNV2S/1000G] [PCIe 4.0 x4, чтение - 3500 Мбайт/сек, запись - 2100 Мбайт/сек, 3 бит TLC, NVM Express, TBW - 320 ТБ]',
            'specs': {
                'capacity': '1000 ГБ',
                'interface': 'PCIe 4.0 x4',
                'read_speed': '3500 Мбайт/сек',
                'write_speed': '2100 Мбайт/сек',
                'type': '3 бит TLC',
                'tbw': '320 ТБ'
            }
        },
        {
            'name': 'Cougar GEX X2 850',
            'category_id': 6,  # Блоки питания
            'price': 10999,
            'price_category_id': 3,  # Премиум
            'description': 'Блок питания Cougar GEX X2 850 [31GT085001P01] черный [850 Вт, 80+ Gold, APFC, 20+4 pin, 4+4 pin, 8 pin CPU, 10 SATA, 16 pin (12VHPWR), 4 x 6+2 pin PCI-E]',
            'specs': {
                'power': '850 Вт',
                'efficiency': '80+ Gold',
                'features': 'APFC',
                'connectors': '20+4 pin, 4+4 pin, 8 pin CPU, 10 SATA, 16 pin (12VHPWR), 4 x 6+2 pin PCI-E'
            }
        },
        {
            'name': 'Cougar FV150 RGB',
            'category_id': 8,  # Корпуса
            'price': 7999,
            'price_category_id': 3,  # Премиум
            'description': 'Корпус Cougar FV150 RGB [FV150 RGB black] черный [Mid-Tower, Micro-ATX, Mini-ITX, Standard-ATX, USB 3.2 Gen 1 Type-A, USB 3.2 Gen 2 Type-C, ARGB вентиляторы, 4 x 120 мм]',
            'specs': {
                'form_factor': 'Mid-Tower',
                'supported_motherboards': 'Micro-ATX, Mini-ITX, Standard-ATX',
                'usb_ports': 'USB 3.2 Gen 1 Type-A, USB 3.2 Gen 2 Type-C',
                'fans': 'ARGB вентиляторы, 4 x 120 мм'
            }
        },
        {
            'name': 'DEEPCOOL AK620 DIGITAL',
            'category_id': 7,  # Охлаждение
            'price': 6999,
            'price_category_id': 3,  # Премиум
            'description': 'Кулер для процессора DEEPCOOL AK620 DIGITAL [R-AK620-BKADMN-G] [основание - медь, 1850 об/мин, 28 дБ, 4 pin, 260 Вт]',
            'specs': {
                'base_material': 'медь',
                'fan_speed': '1850 об/мин',
                'noise_level': '28 дБ',
                'connector': '4 pin',
                'tdp': '260 Вт'
            }
        },
        {
            'name': 'ID-COOLING XF Series',
            'category_id': 7,  # Охлаждение
            'price': 1996,
            'price_category_id': 3,  # Премиум
            'description': 'Вентилятор ID-COOLING XF Series [XF-120-ARGB-K] [120 x 120 мм, 4 pin Male / 4 pin Female, 500 об/мин - 1500 об/мин, 13.8 дБ - 30.5 дБ, в комплекте - 1]',
            'specs': {
                'size': '120 x 120 мм',
                'connector': '4 pin Male / 4 pin Female',
                'speed_range': '500-1500 об/мин',
                'noise_range': '13.8-30.5 дБ',
                'rgb': True
            }
        }
    ]
    
    # Добавляем компоненты
    component_ids = []
    for component in components:
        specs_json = json.dumps(component.get('specs')) if component.get('specs') else None
        component_id = add_component(
            name=component['name'],
            category_id=component['category_id'],
            price=component['price'],
            price_category_id=component['price_category_id'],
            description=component['description'],
            specs=specs_json
        )
        component_ids.append(component_id)
    
    # Создаем сборку
    return add_build(
        name='Игровой ПК DNS (Ryzen 5 7500F + RTX 5070 Ti)',
        device_type_id=1,  # Игровой ПК
        price_category_id=3,  # Премиум
        description='Мощный игровой ПК на базе процессора AMD Ryzen 5 7500F и видеокарты RTX 5070 Ti. Отличный выбор для игр в разрешении 1440p и 4K.',
        link='https://www.dns-shop.ru/user-pc/configuration/1aa529f5cd09801a/',
        component_ids=component_ids
    )

def add_dns_build_4():
    """Добавление новой бюджетной сборки из DNS"""
    # Сначала добавляем компоненты
    components = [
        {
            'name': 'Intel Core i3-12100F OEM',
            'category_id': 1,  # Процессоры
            'price': 5099,
            'price_category_id': 1,  # Бюджетный
            'description': 'Процессор Intel Core i3-12100F OEM [LGA 1700, 4 x 3.3 ГГц, L2 - 5 МБ, L3 - 12 МБ, 2 х DDR4, DDR5-4800 МГц, TDP 89 Вт]',
            'specs': {
                'socket': 'LGA 1700',
                'cores': 4,
                'clock': '3.3 ГГц',
                'l2_cache': '5 МБ',
                'l3_cache': '12 МБ',
                'memory_type': 'DDR4, DDR5-4800 МГц',
                'tdp': '89 Вт'
            }
        },
        {
            'name': 'MSI PRO H610M-E DDR4',
            'category_id': 5,  # Материнские платы
            'price': 5399,
            'price_category_id': 1,  # Бюджетный
            'description': 'Материнская плата MSI PRO H610M-E DDR4 [LGA 1700, Intel H610, 2xDDR4-3200 МГц, 1xPCI-Ex16, 1xM.2, Micro-ATX]',
            'specs': {
                'socket': 'LGA 1700',
                'chipset': 'Intel H610',
                'memory_slots': 2,
                'memory_type': 'DDR4-3200 МГц',
                'pcie_slots': '1xPCI-Ex16',
                'm2_slots': 1,
                'form_factor': 'Micro-ATX'
            }
        },
        {
            'name': 'INNO3D GeForce RTX 3050 TWIN X2 OC',
            'category_id': 2,  # Видеокарты
            'price': 21999,
            'price_category_id': 1,  # Бюджетный
            'description': 'Видеокарта INNO3D GeForce RTX 3050 TWIN X2 OC [PCIe 4.0 8 ГБ GDDR6, 128 бит, DisplayPort, DVI-D, HDMI, GPU 1552 МГц]',
            'specs': {
                'memory': '8 ГБ GDDR6',
                'memory_bus': '128 бит',
                'ports': 'DisplayPort, DVI-D, HDMI',
                'gpu_clock': '1552 МГц',
                'interface': 'PCIe 4.0'
            }
        },
        {
            'name': 'ADATA XPG SPECTRIX D35G RGB 16 ГБ',
            'category_id': 3,  # Оперативная память
            'price': 3599,
            'price_category_id': 1,  # Бюджетный
            'description': 'Оперативная память ADATA XPG SPECTRIX D35G RGB [AX4U32008G16A-DTBKD35G] 16 ГБ [DDR4, 8 ГБx2 шт, 3200 МГц, 16(CL)-20-20]',
            'specs': {
                'capacity': '16 ГБ',
                'modules': '8 ГБx2 шт',
                'type': 'DDR4',
                'speed': '3200 МГц',
                'timings': '16(CL)-20-20',
                'rgb': True
            }
        },
        {
            'name': 'Apacer AS340 PANTHER 480GB',
            'category_id': 4,  # Накопители
            'price': 2550,
            'price_category_id': 1,  # Бюджетный
            'description': '480 ГБ 2.5" SATA накопитель Apacer AS340 PANTHER [AP480GAS340G-1] [SATA, чтение - 550 Мбайт/сек, запись - 520 Мбайт/сек, 3D NAND 3 бит TLC, TBW - 280 ТБ]',
            'specs': {
                'capacity': '480 ГБ',
                'interface': 'SATA',
                'read_speed': '550 Мбайт/сек',
                'write_speed': '520 Мбайт/сек',
                'type': '3D NAND 3 бит TLC',
                'tbw': '280 ТБ'
            }
        },
        {
            'name': 'Cougar XTC600',
            'category_id': 6,  # Блоки питания
            'price': 3299,
            'price_category_id': 1,  # Бюджетный
            'description': 'Блок питания Cougar XTC600 [31XC060.0001P] черный [600 Вт, 80+, APFC, 20+4 pin, 4+4 pin CPU, 6 SATA, 2 x 6+2 pin PCI-E]',
            'specs': {
                'power': '600 Вт',
                'efficiency': '80+',
                'features': 'APFC',
                'connectors': '20+4 pin, 4+4 pin CPU, 6 SATA, 2 x 6+2 pin PCI-E'
            }
        },
        {
            'name': 'ARDOR GAMING Rare Minicase MS2',
            'category_id': 8,  # Корпуса
            'price': 3999,
            'price_category_id': 1,  # Бюджетный
            'description': 'Корпус ARDOR GAMING Rare Minicase MS2 черный [Mini-Tower, Micro-ATX, Mini-ITX, USB 2.0 Type-A, USB 3.2 Gen 1 Type-A]',
            'specs': {
                'form_factor': 'Mini-Tower',
                'supported_motherboards': 'Micro-ATX, Mini-ITX',
                'usb_ports': 'USB 2.0 Type-A, USB 3.2 Gen 1 Type-A',
                'fans': 'нет'
            }
        },
        {
            'name': 'ID-COOLING SE-903-XT ARGB',
            'category_id': 7,  # Охлаждение
            'price': 1099,
            'price_category_id': 1,  # Бюджетный
            'description': 'Кулер для процессора ID-COOLING SE-903-XT ARGB [SE-903-XT ARGB] [основание - алюминий\медь, 2200 об/мин, 25.8 дБ, 4 pin, 130 Вт]',
            'specs': {
                'base_material': 'алюминий\медь',
                'fan_speed': '2200 об/мин',
                'noise_level': '25.8 дБ',
                'connector': '4 pin',
                'tdp': '130 Вт',
                'rgb': True
            }
        }
    ]
    
    # Добавляем компоненты
    component_ids = []
    for component in components:
        specs_json = json.dumps(component.get('specs')) if component.get('specs') else None
        component_id = add_component(
            name=component['name'],
            category_id=component['category_id'],
            price=component['price'],
            price_category_id=component['price_category_id'],
            description=component['description'],
            specs=specs_json
        )
        component_ids.append(component_id)
    
    # Создаем сборку
    return add_build(
        name='Бюджетный игровой ПК DNS (i3-12100F + RTX 3050)',
        device_type_id=1,  # Игровой ПК
        price_category_id=1,  # Бюджетный
        description='Бюджетный игровой ПК на базе процессора Intel Core i3-12100F и видеокарты RTX 3050. Отличный выбор для игр в разрешении 1080p.',
        link='https://www.dns-shop.ru/user-pc/configuration/a32c15b219cf92ba/',
        component_ids=component_ids
    )

def init_basic_data():
    """Инициализация базовых данных (категории, типы устройств, ценовые категории)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Добавляем типы устройств
    device_types = [
        (1, "Игровой ПК", "Компьютеры для игр с высокой производительностью"),
        (2, "Рабочий ПК", "Компьютеры для работы и офисного использования"),
        (3, "Ноутбук", "Портативные компьютеры")
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO device_types (id, name, description)
        VALUES (?, ?, ?)
    """, device_types)
    
    # Добавляем ценовые категории
    price_categories = [
        (1, "Бюджетный", 0, 40000, "Недорогие решения до 40 тыс. рублей"),
        (2, "Средний", 40000, 80000, "Сбалансированные решения от 40 до 80 тыс. рублей"),
        (3, "Премиум", 80000, 500000, "Высокопроизводительные системы от 80 тыс. рублей")
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO price_categories (id, name, min_price, max_price, description)
        VALUES (?, ?, ?, ?, ?)
    """, price_categories)
    
    # Добавляем категории компонентов
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
        INSERT OR REPLACE INTO component_categories (id, name, description)
        VALUES (?, ?, ?)
    """, component_categories)
    
    conn.commit()
    conn.close()
    print("Базовые данные инициализированы")

# Инициализация БД при импорте модуля
init_db()