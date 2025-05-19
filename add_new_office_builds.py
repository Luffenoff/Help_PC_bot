import sqlite3
from database import get_db_connection, add_component, add_build

def add_office_builds():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Сборка 1
    build1_components = [
        {
            "name": "AMD Ryzen 5 3400G OEM",
            "category_id": 1,  # Процессоры
            "price": 6399,
            "price_category_id": 1,  # Бюджетный
            "description": "Процессор AMD Ryzen 5 3400G OEM [AM4, 4 x 3.7 ГГц, L2 - 2 МБ, L3 - 4 МБ, 2 х DDR4-2933 МГц, AMD Radeon Vega 11, TDP 65 Вт]"
        },
        {
            "name": "ASRock B450M-HDV R4.0",
            "category_id": 5,  # Материнские платы
            "price": 5599,
            "price_category_id": 1,
            "description": "Материнская плата ASRock B450M-HDV R4.0 [AM4, AMD B450, 2xDDR4-3200 МГц, 1xPCI-Ex16, 1xM.2, Micro-ATX]"
        },
        {
            "name": "Apacer TEX 16 ГБ",
            "category_id": 3,  # Оперативная память
            "price": 2199,
            "price_category_id": 1,
            "description": "Оперативная память Apacer TEX [AH4U16G32C28YTBAA-1] 16 ГБ [DDR4, 16 ГБx1 шт, 3200 МГц, 16(CL)-20-20-38]"
        },
        {
            "name": "ADATA LEGEND 710 512 ГБ",
            "category_id": 4,  # Накопители
            "price": 2799,
            "price_category_id": 1,
            "description": "512 ГБ M.2 NVMe накопитель ADATA LEGEND 710 [ALEG-710-512GCS] [PCIe 3.0 x4, чтение - 2400 Мбайт/сек, запись - 1600 Мбайт/сек, NVM Express, TBW - 130 ТБ]"
        },
        {
            "name": "Chieftec EON 400W",
            "category_id": 6,  # Блоки питания
            "price": 3299,
            "price_category_id": 1,
            "description": "Блок питания Chieftec EON [ZPU-400S] черный [400 Вт, 80+, APFC, 20+4 pin, 4+4 pin CPU, 4 SATA, 6+2 pin PCI-E]"
        },
        {
            "name": "DEXP DC-101B",
            "category_id": 8,  # Корпуса
            "price": 2899,
            "price_category_id": 1,
            "description": "Корпус DEXP DC-101B черный [Mid-Tower, Micro-ATX, Mini-ITX, Standard-ATX, USB 2.0 Type-A]"
        },
        {
            "name": "ID-COOLING SE-214-XT",
            "category_id": 7,  # Охлаждение
            "price": 1199,
            "price_category_id": 1,
            "description": "Кулер для процессора ID-COOLING SE-214-XT [LGA1700] [основание - алюминий\\медь, 1500 об/мин, 26.6 дБ, 4 pin, 180 Вт]"
        }
    ]

    # Сборка 2
    build2_components = [
        {
            "name": "AMD Ryzen 5 PRO 4655G OEM",
            "category_id": 1,
            "price": 9299,
            "price_category_id": 1,
            "description": "Процессор AMD Ryzen 5 PRO 4655G OEM [AM4, 6 x 3.7 ГГц, L2 - 3 МБ, L3 - 8 МБ, 2 х DDR4-3200 МГц, AMD Radeon Graphics, TDP 65 Вт]"
        },
        {
            "name": "GIGABYTE A520M K V2",
            "category_id": 5,
            "price": 4899,
            "price_category_id": 1,
            "description": "Материнская плата GIGABYTE A520M K V2 [AM4, AMD A520, 2xDDR4-3200 МГц, 1xPCI-Ex16, 1xM.2, Micro-ATX]"
        },
        {
            "name": "Apacer 16 ГБ",
            "category_id": 3,
            "price": 1999,
            "price_category_id": 1,
            "description": "Оперативная память Apacer [EL.16G21.GSH] 16 ГБ [DDR4, 16 ГБx1 шт, 3200 МГц, 22(CL)]"
        },
        {
            "name": "AGI AI238 1000 ГБ",
            "category_id": 4,
            "price": 5099,
            "price_category_id": 1,
            "description": "1000 ГБ 2.5\" SATA накопитель AGI AI238 [AGI1K0GIMAI238] [SATA, чтение - 540 Мбайт/сек, запись - 500 Мбайт/сек, 3D NAND 4 бит QLC]"
        },
        {
            "name": "Cougar STC500 500W",
            "category_id": 6,
            "price": 3499,
            "price_category_id": 1,
            "description": "Блок питания Cougar STC500 500W [CGR SC-500] черный [500 Вт, 80+, APFC, 20+4 pin, 4+4 pin CPU, 5 SATA, 2 x 6+2 pin PCI-E]"
        },
        {
            "name": "DEXP DCV-280B",
            "category_id": 8,
            "price": 2499,
            "price_category_id": 1,
            "description": "Корпус DEXP DCV-280B черный [Mini-Tower, Micro-ATX, Mini-ITX, USB 2.0 Type-A, USB 3.2 Gen 1 Type-C]"
        },
        {
            "name": "ID-COOLING SE-214-XT",
            "category_id": 7,
            "price": 1199,
            "price_category_id": 1,
            "description": "Кулер для процессора ID-COOLING SE-214-XT [LGA1700] [основание - алюминий\\медь, 1500 об/мин, 26.6 дБ, 4 pin, 180 Вт]"
        }
    ]

    # Сборка 3
    build3_components = [
        {
            "name": "AMD Ryzen 5 5500GT OEM",
            "category_id": 1,
            "price": 11699,
            "price_category_id": 1,
            "description": "Процессор AMD Ryzen 5 5500GT OEM [AM4, 6 x 3.6 ГГц, L2 - 3 МБ, L3 - 16 МБ, 2 х DDR4-3200 МГц, AMD Radeon Vega 7, TDP 65 Вт]"
        },
        {
            "name": "GIGABYTE A520M S2H",
            "category_id": 5,
            "price": 5199,
            "price_category_id": 1,
            "description": "Материнская плата GIGABYTE A520M S2H [AM4, AMD A520, 2xDDR4-3200 МГц, 1xPCI-Ex16, 1xM.2, Micro-ATX]"
        },
        {
            "name": "ADATA Premier 16 ГБ",
            "category_id": 3,
            "price": 2199,
            "price_category_id": 1,
            "description": "Оперативная память ADATA Premier [AD4U320016G22-SGN] 16 ГБ [DDR4, 16 ГБx1 шт, 3200 МГц, 22(CL)]"
        },
        {
            "name": "ARDOR GAMING Ally AL1284 512 ГБ",
            "category_id": 4,
            "price": 2899,
            "price_category_id": 1,
            "description": "512 ГБ M.2 NVMe накопитель ARDOR GAMING Ally AL1284 [ALMAYM1024-AL1284] [PCIe 3.0 x4, чтение - 3100 Мбайт/сек, запись - 2700 Мбайт/сек, 3 бит TLC, NVM Express, TBW - 375 ТБ]"
        },
        {
            "name": "Azerty RPL-400GAR",
            "category_id": 6,
            "price": 1999,
            "price_category_id": 1,
            "description": "Блок питания Azerty RPL-400GAR черный [400 Вт, 20+4 pin, 4+4 pin CPU, 4 SATA, 6+2 pin PCI-E]"
        },
        {
            "name": "DEXP DCV-200W",
            "category_id": 8,
            "price": 1999,
            "price_category_id": 1,
            "description": "Корпус DEXP DCV-200W белый [Mini-Tower, Micro-ATX, Mini-ITX, USB 2.0 Type-A, USB 3.2 Gen 1 Type-A]"
        },
        {
            "name": "ID-COOLING SE-903-SD V3",
            "category_id": 7,
            "price": 799,
            "price_category_id": 1,
            "description": "Кулер для процессора ID-COOLING SE-903-SD V3 [основание - алюминий\\медь, 2000 об/мин, 23.1 дБ, 3 pin, 130 Вт]"
        }
    ]

    # Добавляем компоненты и получаем их ID
    component_ids = {}
    for build_components in [build1_components, build2_components, build3_components]:
        for component in build_components:
            if component["name"] not in component_ids:
                component_id = add_component(
                    name=component["name"],
                    category_id=component["category_id"],
                    price=component["price"],
                    price_category_id=component["price_category_id"],
                    description=component["description"]
                )
                component_ids[component["name"]] = component_id

    # Добавляем сборки
    builds = [
        {
            "name": "Офисный ПК на AMD Ryzen 5 3400G",
            "device_type_id": 2,  # Офисный ПК
            "price_category_id": 1,  # Бюджетный
            "description": "Бюджетный офисный ПК на базе процессора AMD Ryzen 5 3400G с интегрированной графикой",
            "link": "https://www.dns-shop.ru/user-pc/configuration/00c44f32e6c8e1af/",
            "components": [component_ids[comp["name"]] for comp in build1_components]
        },
        {
            "name": "Офисный ПК на AMD Ryzen 5 PRO 4655G",
            "device_type_id": 2,
            "price_category_id": 1,
            "description": "Офисный ПК на базе процессора AMD Ryzen 5 PRO 4655G с интегрированной графикой",
            "link": "https://www.dns-shop.ru/user-pc/configuration/7b6867800b12fc17/",
            "components": [component_ids[comp["name"]] for comp in build2_components]
        },
        {
            "name": "Офисный ПК на AMD Ryzen 5 5500GT",
            "device_type_id": 2,
            "price_category_id": 1,
            "description": "Офисный ПК на базе процессора AMD Ryzen 5 5500GT с интегрированной графикой",
            "link": "https://www.dns-shop.ru/user-pc/configuration/400039ff5bcb9657/",
            "components": [component_ids[comp["name"]] for comp in build3_components]
        }
    ]

    for build in builds:
        add_build(
            name=build["name"],
            device_type_id=build["device_type_id"],
            price_category_id=build["price_category_id"],
            description=build["description"],
            link=build["link"],
            component_ids=build["components"]
        )

    conn.close()
    print("Новые офисные сборки успешно добавлены в базу данных")

def add_last_builds():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Сборка 18
    build18_components = [
        {"name": "AMD Athlon 3000G OEM", "category_id": 1, "price": 4299, "price_category_id": 1, "description": "Процессор AMD Athlon 3000G OEM [AM4, 2 x 3.5 ГГц, L2 - 1 МБ, L3 - 4 МБ, 2 х DDR4-2666 МГц, AMD Radeon Vega 3, TDP 35 Вт]"},
        {"name": "ASRock B450M-HDV R4.0", "category_id": 5, "price": 5599, "price_category_id": 1, "description": "Материнская плата ASRock B450M-HDV R4.0 [AM4, AMD B450, 2xDDR4-3200 МГц, 1xPCI-Ex16, 1xM.2, Micro-ATX]"},
        {"name": "Patriot Signature Line 8 ГБ", "category_id": 3, "price": 2100, "price_category_id": 1, "description": "Оперативная память Patriot Signature Line [PSD48G266681] 8 ГБ [DDR4, 8 ГБx1 шт, 2666 МГц, 19(CL)-19-19-43]"},
        {"name": "Apacer AS350 PANTHER 128 ГБ", "category_id": 4, "price": 950, "price_category_id": 1, "description": "128 ГБ 2.5\" SATA накопитель Apacer AS350 PANTHER [95.DB260.P100C] [SATA, чтение - 560 Мбайт/сек, запись - 540 Мбайт/сек, 3D NAND 3 бит TLC, TBW - 75 ТБ]"},
        {"name": "DEEPCOOL GAMMA ARCHER", "category_id": 7, "price": 499, "price_category_id": 1, "description": "Кулер для процессора DEEPCOOL GAMMA ARCHER [DP-MCAL-GA] [основание - алюминий, 1600 об/мин, 26.1 дБ, 3 pin, 95 Вт]"},
        {"name": "AeroCool ECO 450W", "category_id": 6, "price": 2899, "price_category_id": 1, "description": "Блок питания AeroCool ECO 450W серый [450 Вт, 20+4 pin, 4 pin CPU, 2 SATA, 6 pin PCI-E]"},
        {"name": "DEXP DC-101B", "category_id": 8, "price": 2899, "price_category_id": 1, "description": "Корпус DEXP DC-101B черный [Mid-Tower, Micro-ATX, Mini-ITX, Standard-ATX, USB 2.0 Type-A]"},
        {"name": "DEFENDER LINE C-511", "category_id": 8, "price": 599, "price_category_id": 1, "description": "Клавиатура+мышь проводная Defender LINE C-511 черный [кнопок мыши - 3 шт, оптическая светодиодная, USB, Fn]"},
        {"name": "DEXP DF22N2", "category_id": 8, "price": 6799, "price_category_id": 1, "description": "21.45\" Монитор DEXP DF22N2 черный [1920x1080@100 Гц, VA, LED, 3000:1, 250 Кд/м², 178°/178°, HDMI 1.4, VGA (D-Sub)]"}
    ]

    # Сборка 19
    build19_components = [
        {"name": "AMD Ryzen 5 3400G OEM", "category_id": 1, "price": 6399, "price_category_id": 1, "description": "Процессор AMD Ryzen 5 3400G OEM [AM4, 4 x 3.7 ГГц, L2 - 2 МБ, L3 - 4 МБ, 2 х DDR4-2933 МГц, AMD Radeon Vega 11, TDP 65 Вт]"},
        {"name": "ASRock B450M-HDV R4.0", "category_id": 5, "price": 5599, "price_category_id": 1, "description": "Материнская плата ASRock B450M-HDV R4.0 [AM4, AMD B450, 2xDDR4-3200 МГц, 1xPCI-Ex16, 1xM.2, Micro-ATX]"},
        {"name": "ADATA XPG GAMMIX D20 16 ГБ", "category_id": 3, "price": 3099, "price_category_id": 1, "description": "Оперативная память ADATA XPG GAMMIX D20 [AX4U32008G16A-DCBK20] 16 ГБ [DDR4, 8 ГБx2 шт, 3200 МГц, 16(CL)-20-20]"},
        {"name": "ADATA LEGEND 710 512 ГБ", "category_id": 4, "price": 2799, "price_category_id": 1, "description": "512 ГБ M.2 NVMe накопитель ADATA LEGEND 710 [ALEG-710-512GCS] [PCIe 3.0 x4, чтение - 2400 Мбайт/сек, запись - 1600 Мбайт/сек, NVM Express, TBW - 130 ТБ]"},
        {"name": "Chieftec EON 400W", "category_id": 6, "price": 3299, "price_category_id": 1, "description": "Блок питания Chieftec EON [ZPU-400S] черный [400 Вт, 80+, APFC, 20+4 pin, 4+4 pin CPU, 4 SATA, 6+2 pin PCI-E]"},
        {"name": "DEXP DC-101B", "category_id": 8, "price": 2899, "price_category_id": 1, "description": "Корпус DEXP DC-101B черный [Mid-Tower, Micro-ATX, Mini-ITX, Standard-ATX, USB 2.0 Type-A]"},
        {"name": "ID-COOLING SE-214-XT", "category_id": 7, "price": 1199, "price_category_id": 1, "description": "Кулер для процессора ID-COOLING SE-214-XT [LGA1700] [основание - алюминий\\медь, 1500 об/мин, 26.6 дБ, 4 pin, 180 Вт]"}
    ]

    # Сборка 21
    build21_components = [
        {"name": "AMD Ryzen 3 3200G OEM", "category_id": 1, "price": 4999, "price_category_id": 1, "description": "Процессор AMD Ryzen 3 3200G OEM [AM4, 4 x 3.6 ГГц, L2 - 2 МБ, L3 - 4 МБ, 2 х DDR4-2933 МГц, AMD Radeon Vega 8, TDP 65 Вт]"},
        {"name": "ASRock B450M-HDV R4.0", "category_id": 5, "price": 5599, "price_category_id": 1, "description": "Материнская плата ASRock B450M-HDV R4.0 [AM4, AMD B450, 2xDDR4-3200 МГц, 1xPCI-Ex16, 1xM.2, Micro-ATX]"},
        {"name": "Apacer 16 ГБ", "category_id": 3, "price": 1999, "price_category_id": 1, "description": "Оперативная память Apacer [EL.16G21.GSH] 16 ГБ [DDR4, 16 ГБx1 шт, 3200 МГц, 22(CL)]"},
        {"name": "Patriot P300 256 ГБ", "category_id": 4, "price": 1399, "price_category_id": 1, "description": "256 ГБ M.2 NVMe накопитель Patriot P300 [P300P256GM28] [PCIe 3.0 x4, чтение - 1700 Мбайт/сек, запись - 1100 Мбайт/сек, NVM Express, TBW - 120 ТБ]"},
        {"name": "AeroCool ECO 400W", "category_id": 6, "price": 2199, "price_category_id": 1, "description": "Блок питания AeroCool ECO 400W [ECO-400W] серый [400 Вт, 20+4 pin, 4 pin CPU, 2 SATA, 6 pin PCI-E]"},
        {"name": "DEXP DC-202M", "category_id": 8, "price": 1950, "price_category_id": 1, "description": "Корпус DEXP DC-202M черный [Mini-Tower, Micro-ATX, Mini-ITX, USB 2.0 Type-A]"},
        {"name": "DEEPCOOL GAMMA ARCHER", "category_id": 7, "price": 499, "price_category_id": 1, "description": "Кулер для процессора DEEPCOOL GAMMA ARCHER [DP-MCAL-GA] [основание - алюминий, 1600 об/мин, 26.1 дБ, 3 pin, 95 Вт]"},
        {"name": "DEFENDER Patch MS-759", "category_id": 8, "price": 150, "price_category_id": 1, "description": "Мышь проводная Defender Patch MS-759 [52759] черный [1000 dpi, светодиодный, USB Type-A, кнопки - 3]"},
        {"name": "Aceline K-1204BU", "category_id": 8, "price": 350, "price_category_id": 1, "description": "Клавиатура проводная Aceline K-1204BU [мембранная, клавиш - 104, USB Type-A, черный]"},
        {"name": "DEXP DF22N2", "category_id": 8, "price": 6799, "price_category_id": 1, "description": "21.45\" Монитор DEXP DF22N2 черный [1920x1080@100 Гц, VA, LED, 3000:1, 250 Кд/м², 178°/178°, HDMI 1.4, VGA (D-Sub)]"},
        {"name": "GoPower HDMI-HDMI 1.5м", "category_id": 8, "price": 120, "price_category_id": 1, "description": "Кабель GoPower HDMI - HDMI, 1.5 м [вилка - вилка, версия 1.4, длина - 1.5 м, 1920x1080, 60 Гц]"},
        {"name": "DEXP Standard 418B", "category_id": 8, "price": 399, "price_category_id": 1, "description": "Сетевой фильтр DEXP Standard 418B черный [розетки - 4, 10 А, 2400 Вт, кабель - 1.8 м]"}
    ]

    # Добавляем компоненты и получаем их ID
    component_ids = {}
    for build_components in [build18_components, build19_components, build21_components]:
        for component in build_components:
            if component["name"] not in component_ids:
                component_id = add_component(
                    name=component["name"],
                    category_id=component["category_id"],
                    price=component["price"],
                    price_category_id=component["price_category_id"],
                    description=component["description"]
                )
                component_ids[component["name"]] = component_id

    # Добавляем сборки
    builds = [
        {
            "name": "Офисный ПК на Athlon 3000G (с периферией)",
            "device_type_id": 2,
            "price_category_id": 1,
            "description": "Офисный ПК на базе Athlon 3000G с периферией и монитором",
            "link": "https://www.dns-shop.ru/user-pc/configuration/47d7e6541d06bf0a/",
            "components": [component_ids[comp["name"]] for comp in build18_components]
        },
        {
            "name": "Офисный ПК на Ryzen 5 3400G (XPG D20)",
            "device_type_id": 2,
            "price_category_id": 1,
            "description": "Офисный ПК на базе Ryzen 5 3400G с памятью XPG D20",
            "link": "https://www.dns-shop.ru/user-pc/configuration/9afa20044469d27a/",
            "components": [component_ids[comp["name"]] for comp in build19_components]
        },
        {
            "name": "Офисный ПК на Ryzen 3 3200G (с периферией)",
            "device_type_id": 2,
            "price_category_id": 1,
            "description": "Офисный ПК на базе Ryzen 3 3200G с периферией и монитором",
            "link": "https://www.dns-shop.ru/user-pc/configuration/294235108de15b54/",
            "components": [component_ids[comp["name"]] for comp in build21_components]
        }
    ]

    for build in builds:
        add_build(
            name=build["name"],
            device_type_id=build["device_type_id"],
            price_category_id=build["price_category_id"],
            description=build["description"],
            link=build["link"],
            component_ids=build["components"]
        )

    conn.close()
    print("Последние офисные сборки с периферией успешно добавлены в базу данных")

if __name__ == "__main__":
    add_office_builds()
    add_last_builds() 