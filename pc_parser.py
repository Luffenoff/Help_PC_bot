import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PCParser:
    def __init__(self):
        self.pc_builds = []
        print("Инициализация парсера...")
        self.setup_driver()
        self.load_data()
        print(f"Всего сборок после инициализации: {len(self.pc_builds)}")

    def setup_driver(self):
        """Настройка драйвера Selenium"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Запуск в фоновом режиме
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.wait = WebDriverWait(self.driver, 20)  # Увеличиваем время ожидания

    def load_data(self):
        """Загрузка данных из файла"""
        try:
            with open('pc_builds.json', 'r', encoding='utf-8') as f:
                self.pc_builds = json.load(f)
                print(f"Загружено {len(self.pc_builds)} сборок из файла")
        except FileNotFoundError:
            print("Файл с данными не найден, добавляем тестовые данные")
            self.add_test_data()
            self.save_to_json()
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            print("Добавляем тестовые данные")
            self.add_test_data()
            self.save_to_json()

    def update_data(self):
        """Обновление данных с сайтов"""
        print("Начинаем обновление данных...")
        try:
            # Сохраняем старые данные
            old_builds = self.pc_builds.copy()
            
            # Очищаем список и добавляем тестовые данные
            self.pc_builds = []
            self.add_test_data()
            
            # Пробуем получить новые данные
            self.parse_regard()  # Начинаем с Regard.ru
            time.sleep(2)  # Задержка между запросами
            
            self.parse_dns()
            time.sleep(2)
            
            self.parse_citilink()
            time.sleep(2)
            
            self.parse_mvideo()
            
            # Если не удалось получить новые данные, возвращаем старые
            if len(self.pc_builds) <= len(old_builds):
                print("Не удалось получить новые данные, используем старые")
                self.pc_builds = old_builds
            else:
                print(f"Успешно обновлены данные. Новых сборок: {len(self.pc_builds)}")
            
            # Сохраняем обновленные данные
            self.save_to_json()
            
        except Exception as e:
            print(f"Ошибка при обновлении данных: {e}")
            print("Используем существующие данные")

    def add_test_data(self):
        """Добавление тестовых данных"""
        test_builds = [
            {
                'title': 'Игровой ПК AMD Ryzen 5 5600X, RTX 3060, 16GB RAM',
                'price': '95000',
                'url': 'https://example.com/pc1',
                'source': 'Тестовый магазин',
                'type': 'pc',
                'purpose': 'gaming',
                'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'title': 'Рабочая станция Intel Core i5 12400F, 32GB RAM',
                'price': '85000',
                'url': 'https://example.com/pc2',
                'source': 'Тестовый магазин',
                'type': 'pc',
                'purpose': 'work',
                'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'title': 'Ноутбук Lenovo IdeaPad Gaming 3',
                'price': '75000',
                'url': 'https://example.com/laptop1',
                'source': 'Тестовый магазин',
                'type': 'laptop',
                'purpose': 'gaming',
                'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'title': 'Ноутбук HP Pavilion 15',
                'price': '65000',
                'url': 'https://example.com/laptop2',
                'source': 'Тестовый магазин',
                'type': 'laptop',
                'purpose': 'work',
                'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        self.pc_builds = test_builds  # Заменяем список вместо добавления
        print("Добавлены тестовые данные:")
        for build in test_builds:
            print(f"- {build['title']} ({build['price']} руб.)")

    def close(self):
        """Закрытие драйвера"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def parse_dns(self):
        """Парсинг сборок ПК с DNS"""
        try:
            url = "https://www.dns-shop.ru/catalog/17a8a01d16404e77/sborki-pk/"
            print("Парсинг DNS...")
            self.driver.get(url)
            
            # Ждем загрузки элементов
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'catalog-product')))
            
            # Получаем HTML после загрузки
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            builds = soup.find_all('div', class_='catalog-product')
            print(f"Найдено сборок на DNS: {len(builds)}")
            
            for build in builds:
                try:
                    title = build.find('a', class_='catalog-product__name')
                    if not title:
                        continue
                    title = title.text.strip()
                    
                    price = build.find('div', class_='product-buy__price')
                    if not price:
                        continue
                    price = price.text.strip()
                    
                    url = build.find('a', class_='catalog-product__name')['href']
                    if not url.startswith('http'):
                        url = 'https://www.dns-shop.ru' + url
                    
                    print(f"Найдена сборка: {title} - {price}")
                    
                    build_data = {
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'DNS',
                        'type': 'pc',
                        'purpose': 'work',
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
            print("Парсинг Citilink...")
            self.driver.get(url)
            
            # Ждем загрузки элементов
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ProductCardHorizontal')))
            
            # Получаем HTML после загрузки
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            builds = soup.find_all('div', class_='ProductCardHorizontal')
            print(f"Найдено сборок на Citilink: {len(builds)}")
            
            for build in builds:
                try:
                    title = build.find('a', class_='ProductCardHorizontal__title')
                    if not title:
                        continue
                    title = title.text.strip()
                    
                    price = build.find('span', class_='ProductCardHorizontal__price_current-price')
                    if not price:
                        continue
                    price = price.text.strip()
                    
                    url = build.find('a', class_='ProductCardHorizontal__title')['href']
                    if not url.startswith('http'):
                        url = 'https://www.citilink.ru' + url
                    
                    print(f"Найдена сборка: {title} - {price}")
                    
                    build_data = {
                        'title': title,
                        'price': price,
                        'url': url,
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
            print(f"Ошибка при парсинге Citilink: {e}")

    def parse_mvideo(self):
        """Парсинг сборок ПК с М.Видео"""
        try:
            url = "https://www.mvideo.ru/kompyutery/sborki-pk"
            print("Парсинг М.Видео...")
            self.driver.get(url)
            
            # Ждем загрузки элементов
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-grid__item')))
            
            # Получаем HTML после загрузки
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            builds = soup.find_all('div', class_='product-grid__item')
            print(f"Найдено сборок на М.Видео: {len(builds)}")
            
            for build in builds:
                try:
                    title = build.find('a', class_='product-title__text')
                    if not title:
                        continue
                    title = title.text.strip()
                    
                    price = build.find('span', class_='price__main-value')
                    if not price:
                        continue
                    price = price.text.strip()
                    
                    url = build.find('a', class_='product-title__text')['href']
                    if not url.startswith('http'):
                        url = 'https://www.mvideo.ru' + url
                    
                    print(f"Найдена сборка: {title} - {price}")
                    
                    build_data = {
                        'title': title,
                        'price': price,
                        'url': url,
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

    def parse_regard(self):
        """Парсинг сборок ПК с Regard.ru"""
        try:
            url = "https://www.regard.ru/catalog/group4000.htm"
            print("Парсинг Regard.ru...")
            self.driver.get(url)
            
            # Ждем загрузки элементов
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'b-content__main-item')))
            
            # Получаем HTML после загрузки
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            builds = soup.find_all('div', class_='b-content__main-item')
            print(f"Найдено сборок на Regard.ru: {len(builds)}")
            
            for build in builds:
                try:
                    title = build.find('a', class_='b-content__main-item-title')
                    if not title:
                        continue
                    title = title.text.strip()
                    
                    price = build.find('span', class_='price')
                    if not price:
                        continue
                    price = price.text.strip()
                    
                    url = build.find('a', class_='b-content__main-item-title')['href']
                    if not url.startswith('http'):
                        url = 'https://www.regard.ru' + url
                    
                    print(f"Найдена сборка: {title} - {price}")
                    
                    build_data = {
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'Regard.ru',
                        'type': 'pc',
                        'purpose': 'work',
                        'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.pc_builds.append(build_data)
                except Exception as e:
                    print(f"Ошибка при парсинге сборки Regard.ru: {e}")
                    continue

        except Exception as e:
            print(f"Ошибка при парсинге Regard.ru: {e}")

    def get_random_build(self, budget, purpose='work', type='pc'):
        """Получение случайной сборки по бюджету и назначению"""
        try:
            print(f"\nПоиск сборки для бюджета {budget} руб., типа {type}, назначение {purpose}")
            print(f"Всего доступных сборок: {len(self.pc_builds)}")
            
            if not self.pc_builds:
                print("Нет доступных сборок, обновляем данные...")
                self.update_data()
                if not self.pc_builds:
                    print("Не удалось получить данные")
                    return None
            
            df = pd.DataFrame(self.pc_builds)
            print("\nДоступные сборки:")
            for _, row in df.iterrows():
                print(f"- {row['title']} ({row['price']} руб.)")
            
            # Преобразуем цены в числовой формат
            def clean_price(price):
                try:
                    if isinstance(price, (int, float)):
                        return float(price)
                    # Удаляем все символы кроме цифр и точки
                    cleaned = re.sub(r'[^\d.]', '', str(price))
                    if not cleaned:
                        return 0
                    print(f"Преобразование цены: {price} -> {cleaned}")
                    return float(cleaned)
                except Exception as e:
                    print(f"Ошибка при обработке цены {price}: {e}")
                    return 0
            
            df['price'] = df['price'].apply(clean_price)
            
            # Фильтруем по бюджету в диапазоне от 65% до 100%
            min_budget = budget * 0.65
            max_budget = budget
            filtered_df = df[
                (df['price'] > 0) &  # Исключаем нулевые цены
                (df['price'] >= min_budget) &  # Минимальная цена 65% от бюджета
                (df['price'] <= max_budget) &  # Максимальная цена 100% от бюджета
                (df['type'] == type) &
                (df['purpose'] == purpose)
            ]
            
            print(f"\nДиапазон цен: от {min_budget:.0f} до {max_budget:.0f} руб.")
            print(f"Подходящих сборок: {len(filtered_df)}")
            if len(filtered_df) > 0:
                print("Найденные сборки:")
                for _, row in filtered_df.iterrows():
                    print(f"- {row['title']} ({row['price']} руб.)")
            
            if len(filtered_df) == 0:
                print(f"Не найдено сборок в диапазоне от {min_budget:.0f} до {max_budget:.0f} руб., типа {type} и назначения {purpose}")
                return None
                
            # Выбираем случайную сборку
            random_build = filtered_df.sample(n=1).iloc[0]
            print(f"\nВыбрана сборка: {random_build['title']} ({random_build['price']} руб.)")
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

def main():
    parser = PCParser()
    try:
        print("Начинаем парсинг сборок ПК...")
        parser.parse_regard()
        parser.parse_dns()
        parser.parse_citilink()
        parser.parse_mvideo()
        parser.save_to_csv()
        parser.save_to_json()
        print("Парсинг завершен успешно!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main() 