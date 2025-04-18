import json
from database import (
    add_build,
    get_device_types,
    get_price_categories,
    get_components_by_category
)

class BuildLinkManager:
    def __init__(self):
        self.device_types = {type_["name"]: type_["id"] for type_ in get_device_types()}
        self.price_categories = {cat["name"]: cat["id"] for cat in get_price_categories()}
    
    def add_build_from_link(self, build_data):
        """
        Добавление сборки из ссылки
        
        Формат build_data:
        {
            "name": "Название сборки",
            "device_type": "Тип устройства (игровой ПК/рабочий ПК/ноутбук)",
            "price_category": "Ценовая категория (дешево/средне/дорого)",
            "description": "Описание сборки",
            "components": [
                {
                    "name": "Название компонента",
                    "category": "Категория компонента",
                    "price": 10000,
                    "link": "https://example.com/component",
                    "description": "Описание компонента"
                },
                ...
            ],
            "image_url": "https://example.com/image.jpg"
        }
        """
        try:
            # Получаем ID типа устройства и ценовой категории
            device_type_id = self.device_types.get(build_data["device_type"])
            price_category_id = self.price_categories.get(build_data["price_category"])
            
            if not device_type_id or not price_category_id:
                return False, "Неверный тип устройства или ценовая категория"
            
            # Добавляем сборку
            build_id = add_build(
                name=build_data["name"],
                device_type_id=device_type_id,
                price_category_id=price_category_id,
                description=build_data["description"],
                image_url=build_data.get("image_url")
            )
            
            return True, f"Сборка успешно добавлена с ID: {build_id}"
            
        except Exception as e:
            return False, f"Ошибка при добавлении сборки: {str(e)}"
    
    def get_build_template(self):
        """Возвращает шаблон для добавления новой сборки"""
        return {
            "name": "",
            "device_type": "игровой ПК",  # или "рабочий ПК", "ноутбук"
            "price_category": "дешево",   # или "средне", "дорого"
            "description": "",
            "components": [
                {
                    "name": "",
                    "category": "",
                    "price": 0,
                    "link": "",
                    "description": ""
                }
            ],
            "image_url": ""
        } 