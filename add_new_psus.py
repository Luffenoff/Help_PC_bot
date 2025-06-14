from database import add_component, get_db_connection

def add_psus():
    """Добавление новых блоков питания в базу данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем ID категории блоков питания
    cursor.execute("SELECT id FROM component_categories WHERE name = 'Блоки питания'")
    category_id = cursor.fetchone()["id"]
    
    psus = [
        {
            "name": "Блок питания DEEPCOOL PF750 черный",
            "description": "Сертификат 80+ STANDART\n750 Вт, 80+, APFC, 20+4 pin, 2 x 4+4 pin CPU, 6 SATA, 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/5117a7c5fa5fd763/blok-pitania-deepcool-pf750-r-pf750d-ha0b-eu-cernyj/"
        },
        {
            "name": "Блок питания Cougar GEX850 [31GE085001P01] черный",
            "description": "Сертификат 80+ GOLD\n850 Вт, 80+ Gold, APFC, 20+4 pin, 2 x 4+4 pin CPU, 8 SATA, 6 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/2cc61ff0d0bc3332/blok-pitania-cougar-gex850-31ge085001p01-cernyj/"
        },
        {
            "name": "Блок питания DEEPCOOL PF600 черный",
            "description": "Сертификат 80+ STANDART\n600 Вт, 80+, APFC, 20+4 pin, 2 x 4+4 pin CPU, 6 SATA, 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/16ed5812fa5ed763/blok-pitania-deepcool-pf600-r-pf600d-ha0b-eu-cernyj/"
        },
        {
            "name": "Блок питания DEEPCOOL PF650 [R-PF650D-HA0B-EU] черный",
            "description": "Сертификат 80+ STANDART\n650 Вт, 80+, APFC, 20+4 pin, 2 x 4+4 pin CPU, 6 SATA, 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/759476c1fa5ed763/blok-pitania-deepcool-pf650-r-pf650d-ha0b-eu-cernyj/"
        },
        {
            "name": "Блок питания Cougar VTE 600W V2 [CGR BS-600] черный",
            "description": "Сертификат 80+ BRONZE\n600 Вт, 80+ Bronze, APFC, 20+4 pin, 4+4 pin CPU, 6 SATA, 2 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/f3de275402c4d582/blok-pitania-cougar-vte-600w-v2-cgr-bs-600-cernyj/"
        },
        {
            "name": "Блок питания MSI MPG A850G PCIE5 [306-7ZP7B11-CE0] черный",
            "description": "Сертификат 80+ GOLD\n850 Вт, 80+ Gold, APFC, 20+4 pin, 2 x 4+4 pin CPU, 8 SATA, 16 pin (12VHPWR), 6 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/78f2c2318febed20/blok-pitania-msi-mpg-a850g-pcie5-306-7zp7b11-ce0-cernyj/"
        },
        {
            "name": "Блок питания Cougar GEX X2 1000 1000W [GEX X2 1000] черный",
            "description": "Сертификат 80+ GOLD\n1000 Вт, 80+ Gold, APFC, 20+4 pin, 4+4 pin, 8 pin CPU, 12 SATA, 16 pin (12VHPWR), 6 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/3becd83f6bd1ed20/blok-pitania-cougar-gex-x2-1000-1000w-gex-x2-1000-cernyj/"
        },
        {
            "name": "Блок питания Cougar GLE 1200 [CGR GMX-1200] черный",
            "description": "Сертификат 80+ GOLD\n1200 Вт, 80+ Gold, APFC, 20+4 pin, 2 x 4+4 pin CPU, 12 SATA, 16 pin (12V-2x6), 6 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/595d0007ed8bd21a/blok-pitania-cougar-gle-1200-cgr-gmx-1200-cernyj/"
        },
        {
            "name": "Блок питания DEEPCOOL PK650D [R-PK650D-FA0B-EU] черный",
            "description": "Сертификат 80+ BRONZE\n650 Вт, 80+ Bronze, APFC, 20+4 pin, 2 x 4+4 pin CPU, 7 SATA, 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/5e7bfbcba9b9ed20/blok-pitania-deepcool-pk650d-r-pk650d-fa0b-eu-cernyj/"
        },
        {
            "name": "Блок питания DEEPCOOL PL750D [R-PL750D-FC0B-WDEU-V2] черный",
            "description": "Сертификат 80+ BRONZE\n750 Вт, 80+ Bronze, APFC, 20+4 pin, 2 x 4+4 pin CPU, 8 SATA, 16 pin (12VHPWR), 3 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/c92789e28131d582/blok-pitania-deepcool-pl750d-r-pl750d-fc0b-wdeu-v2-cernyj/"
        },
        {
            "name": "Блок питания MSI MAG A750GL PCIE5 черный",
            "description": "Сертификат 80+ GOLD\n750 Вт, 80+ Gold, APFC, 20+4 pin, 2 x 4+4 pin CPU, 8 SATA, 16 pin (12VHPWR), 3 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/18d4de49d482ed20/blok-pitania-msi-mag-a750gl-pcie5--cernyj/"
        },
        {
            "name": "Блок питания Cougar GX 800W [CGR GX-800] черный",
            "description": "Сертификат 80+ GOLD\n800 Вт, 80+ Gold, APFC, 20+4 pin, 4+4 pin, 8 pin CPU, 10 SATA, 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/c02358637c8d3361/blok-pitania-cougar-gx-800w-cgr-gx-800-cernyj/"
        },
        {
            "name": "Блок питания MONTECH GAMMA II 650 [GAMMA II 650] черный",
            "description": "Сертификат 80+ GOLD\n650 Вт, 80+ Gold, APFC, 20+4 pin, 2 x 4+4 pin CPU, 8 SATA, 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/b23177733bb8ed20/blok-pitania-montech-gamma-ii-650-gamma-ii-650-cernyj/"
        },
        {
            "name": "Блок питания DEEPCOOL GamerStorm PN850M WH [R-PN850M-FC0W-WGEU] белый",
            "description": "Сертификат 80+ GOLD\n850 Вт, 80+ Gold, APFC, 20+4 pin, 2 x 4+4 pin CPU, 8 SATA, 16 pin (12V-2x6), 3 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/92839c40a7b1d21a/blok-pitania-deepcool-gamerstorm-pn850m-wh-r-pn850m-fc0w-wgeu-belyj/"
        },
        {
            "name": "Блок питания Cougar GEC SNOW 750 [31GC0750002PR01] белый",
            "description": "Сертификат 80+ GOLD\n750 Вт, 80+ Gold, 20+4 pin, 4+4 pin, 8 pin CPU, 6 SATA, 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/c4f8d3a771f8ed20/blok-pitania-cougar-gec-snow-750-31gc0750002pr01-belyj/"
        },
        {
            "name": "Блок питания Xilence Red Wings XN052 500W [XP500R7] черный",
            "description": "500 Вт, PPFC, 20+4 pin, 4+4 pin CPU, 4 SATA, 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/2b93c24773713330/blok-pitania-xilence-red-wings-xn052-500w-xp500r7-cernyj/"
        },
        {
            "name": "Блок питания ZALMAN GigaMax (GVII) 750W [ZM750-GVII] черный",
            "description": "Сертификат 80+ BRONZE\n750 Вт, 80+ Bronze, APFC, 20+4 pin, 4+4 pin CPU, 5 SATA, 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/09b4b1bffc5b3332/blok-pitania-zalman-gigamax-gvii-750w-zm750-gvii-cernyj/"
        },
        {
            "name": "Блок питания ARDOR GAMING Colossus 850WPF Platinum черный",
            "description": "Сертификат 80+ PLATINUM\n850 Вт, 80+ Platinum, APFC, 20+4 pin, 2 x 4+4 pin CPU, 8 SATA, 16 pin (12VHPWR), 4 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/b330e36a5144a543/blok-pitania-ardor-gaming-colossus-850wpf-platinum--cernyj/"
        },
        {
            "name": "Блок питания ZALMAN MegaMax (TXll) [ZM600-TXII] черный",
            "description": "Сертификат 80+ STANDART\n600 Вт, 80+, APFC, 20+4 pin, 4 pin, 8 pin CPU, 6 SATA, 2 x 6+2 pin PCI-E",
            "link": "https://www.dns-shop.ru/product/09b4b1c1fc5b3332/blok-pitania-zalman-megamax-txll-zm600-txii-cernyj/"
        }
    ]
    
    # Добавляем блоки питания в базу данных
    for psu in psus:
        add_component(
            name=psu["name"],
            category_id=category_id,
            price=0,  # Цена не указана
            price_category_id=1,  # Бюджетная категория по умолчанию
            description=psu["description"],
            specs={"link": psu["link"]}
        )
    
    conn.close()
    print("Новые блоки питания успешно добавлены в базу данных")

if __name__ == "__main__":
    add_psus() 