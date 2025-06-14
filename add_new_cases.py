from database import add_component, get_db_connection

def add_cases():
    """Добавление новых корпусов в базу данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем ID категории корпусов
    cursor.execute("SELECT id FROM component_categories WHERE name = 'Корпуса'")
    category_id = cursor.fetchone()["id"]
    
    # Список корпусов
    cases = [
        {
            "name": "Корпус ZALMAN N4 Rev.1 черный",
            "description": "Форм-фактор: Mid-Tower\nМатериал: Сталь, пластик\nРазмеры: 190x440x480 мм\nВентиляторы: 1x120 мм (в комплекте)\nUSB: 2x USB 2.0, 1x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-zalman-n4-rev1-cernyj/"
        },
        {
            "name": "Корпус Cougar Duoface Pro RGB [CGR-5AD1B-RGB] черный",
            "description": "Форм-фактор: Mid-Tower\nМатериал: Сталь, пластик\nРазмеры: 210x450x490 мм\nВентиляторы: 3x120 мм RGB (в комплекте)\nUSB: 2x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-cougar-duoface-pro-rgb-cgr-5ad1b-rgb-cernyj/"
        },
        {
            "name": "Корпус DEEPCOOL MATREXX 55 MESH черный",
            "description": "Форм-фактор: Mid-Tower\nМатериал: Сталь, пластик\nРазмеры: 200x460x470 мм\nВентиляторы: 1x120 мм (в комплекте)\nUSB: 2x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-deepcool-matrexx-55-mesh-cernyj/"
        },
        {
            "name": "Корпус be quiet! Pure Base 500 черный",
            "description": "Форм-фактор: Mid-Tower\nМатериал: Сталь, пластик\nРазмеры: 190x450x460 мм\nВентиляторы: 2x120 мм (в комплекте)\nUSB: 2x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-be-quiet-pure-base-500-cernyj/"
        },
        {
            "name": "Корпус Fractal Design Meshify C черный",
            "description": "Форм-фактор: Mid-Tower\nМатериал: Сталь, пластик\nРазмеры: 185x440x465 мм\nВентиляторы: 2x120 мм (в комплекте)\nUSB: 2x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-fractal-design-meshify-c-cernyj/"
        },
        {
            "name": "Корпус Lian Li O11 Dynamic черный",
            "description": "Форм-фактор: Full-Tower\nМатериал: Сталь, стекло\nРазмеры: 285x445x465 мм\nВентиляторы: Нет (в комплекте)\nUSB: 2x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX, E-ATX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-lian-li-o11-dynamic-cernyj/"
        },
        {
            "name": "Корпус Phanteks Eclipse P400A черный",
            "description": "Форм-фактор: Mid-Tower\nМатериал: Сталь, пластик\nРазмеры: 200x465x470 мм\nВентиляторы: 2x120 мм (в комплекте)\nUSB: 2x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-phanteks-eclipse-p400a-cernyj/"
        },
        {
            "name": "Корпус NZXT H510 черный",
            "description": "Форм-фактор: Mid-Tower\nМатериал: Сталь, пластик\nРазмеры: 190x428x460 мм\nВентиляторы: 2x120 мм (в комплекте)\nUSB: 1x USB 3.1 Type-C, 1x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-nzxt-h510-cernyj/"
        },
        {
            "name": "Корпус Cooler Master MasterBox MB511 черный",
            "description": "Форм-фактор: Mid-Tower\nМатериал: Сталь, пластик\nРазмеры: 210x468x470 мм\nВентиляторы: 3x120 мм (в комплекте)\nUSB: 2x USB 3.0\nСовместимость: ATX, Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-cooler-master-masterbox-mb511-cernyj/"
        },
        {
            "name": "Корпус Thermaltake Versa H18 черный",
            "description": "Форм-фактор: Mini-Tower\nМатериал: Сталь, пластик\nРазмеры: 180x380x380 мм\nВентиляторы: 1x120 мм (в комплекте)\nUSB: 2x USB 3.0\nСовместимость: Micro-ATX, Mini-ITX",
            "link": "https://www.dns-shop.ru/product/5a7c6c0c0c0c0c0c/korpus-thermaltake-versa-h18-cernyj/"
        }
    ]
    
    # Добавляем корпуса в базу данных
    for case in cases:
        add_component(
            name=case["name"],
            category_id=category_id,
            price=0,  # Цена не указана
            price_category_id=1,  # Бюджетная категория по умолчанию
            description=case["description"],
            specs={"link": case["link"]}  # Сохраняем ссылку в спецификациях
        )
    
    conn.close()
    print("Новые корпуса успешно добавлены в базу данных")

if __name__ == "__main__":
    add_cases() 