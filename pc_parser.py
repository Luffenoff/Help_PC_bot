import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import json
from datetime import datetime
import random

class PCParser:
    def __init__(self):
        self.setup_driver()
        self.pc_builds = []

    def setup_driver(self):
        """Настройка Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def parse_dns(self):
        """Парсинг сборок ПК с DNS"""
        try:
            url = "https://www.dns-shop.ru/catalog/17a8a01d16404e77/sborki-pk/"
            self.driver.get(url)
            time.sleep(5)  # Ждем загрузку страницы

            # Находим все карточки сборок
            builds = self.driver.find_elements(By.CLASS_NAME, "catalog-product")
            
            for build in builds:
                try:
                    build_data = {
                        'title': build.find_element(By.CLASS_NAME, "catalog-product__name").text,
                        'price': build.find_element(By.CLASS_NAME, "product-buy__price").text,
                        'url': build.find_element(By.CLASS_NAME, "catalog-product__name").get_attribute("href"),
                        'source': 'DNS',
                        'type': 'pc',  # По умолчанию ПК
                        'purpose': 'work',  # По умолчанию для работы
                        'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.pc_builds.append(build_data)
                except Exception as e:
                    print(f"Ошибка при парсинге сборки DNS: {e}")
                    continue

        except Exception as e:
            print(f"Ошибка при парсинге DNS: {e}")

    def parse_citilink(self):
        """Парсинг сборок ПК с Ситилинк"""
        try:
            url = "https://www.citilink.ru/catalog/sborki-pk/"
            self.driver.get(url)
            time.sleep(5)

            builds = self.driver.find_elements(By.CLASS_NAME, "ProductCardHorizontal")
            
            for build in builds:
                try:
                    build_data = {
                        'title': build.find_element(By.CLASS_NAME, "ProductCardHorizontal__title").text,
                        'price': build.find_element(By.CLASS_NAME, "ProductCardHorizontal__price").text,
                        'url': build.find_element(By.CLASS_NAME, "ProductCardHorizontal__title").get_attribute("href"),
                        'source': 'Ситилинк',
                        'type': 'pc',
                        'purpose': 'work',
                        'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.pc_builds.append(build_data)
                except Exception as e:
                    print(f"Ошибка при парсинге сборки Ситилинк: {e}")
                    continue

        except Exception as e:
            print(f"Ошибка при парсинге Ситилинк: {e}")

    def parse_mvideo(self):
        """Парсинг сборок ПК с М.Видео"""
        try:
            url = "https://www.mvideo.ru/kompyutery/sborki-pk"
            self.driver.get(url)
            time.sleep(5)

            builds = self.driver.find_elements(By.CLASS_NAME, "product-grid__item")
            
            for build in builds:
                try:
                    build_data = {
                        'title': build.find_element(By.CLASS_NAME, "product-title__text").text,
                        'price': build.find_element(By.CLASS_NAME, "price__main-value").text,
                        'url': build.find_element(By.CLASS_NAME, "product-title__text").get_attribute("href"),
                        'source': 'М.Видео',
                        'type': 'pc',
                        'purpose': 'work',
                        'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.pc_builds.append(build_data)
                except Exception as e:
                    print(f"Ошибка при парсинге сборки М.Видео: {e}")
                    continue

        except Exception as e:
            print(f"Ошибка при парсинге М.Видео: {e}")

    def get_random_build(self, budget, purpose='work', type='pc'):
        """Получение случайной сборки по бюджету и назначению"""
        try:
            df = pd.DataFrame(self.pc_builds)
            # Фильтруем по бюджету, типу и назначению
            filtered_df = df[
                (df['price'].astype(float) <= budget) &
                (df['type'] == type) &
                (df['purpose'] == purpose)
            ]
            
            if len(filtered_df) == 0:
                return None
                
            # Выбираем случайную сборку
            random_build = filtered_df.sample(n=1).iloc[0]
            return random_build.to_dict()
        except Exception as e:
            print(f"Ошибка при выборе случайной сборки: {e}")
            return None

    def save_to_csv(self, filename="pc_builds.csv"):
        """Сохранение данных в CSV файл"""
        df = pd.DataFrame(self.pc_builds)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Данные сохранены в {filename}")

    def save_to_json(self, filename="pc_builds.json"):
        """Сохранение данных в JSON файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.pc_builds, f, ensure_ascii=False, indent=4)
        print(f"Данные сохранены в {filename}")

    def close(self):
        """Закрытие браузера"""
        self.driver.quit()

def main():
    parser = PCParser()
    try:
        print("Начинаем парсинг сборок ПК...")
        parser.parse_dns()
        parser.parse_citilink()
        parser.parse_mvideo()
        parser.save_to_csv()
        parser.save_to_json()
        print("Парсинг завершен успешно!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        parser.close()

if __name__ == "__main__":
    main() 