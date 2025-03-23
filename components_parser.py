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
import json
from datetime import datetime
import random

class ComponentsParser:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.components = []

    def parse_dns_components(self, category):
        """Парсинг комплектующих с DNS"""
        try:
            category_urls = {
                'cpu': 'https://www.dns-shop.ru/catalog/17a8a01cd1644e77/processory/',
                'gpu': 'https://www.dns-shop.ru/catalog/17a897f20e332332/videokarty/',
                'motherboard': 'https://www.dns-shop.ru/catalog/17a89aabdeec9e29/materinskie-platy/',
                'ram': 'https://www.dns-shop.ru/catalog/17a8a01cd1644e77/operativnaya-pamyat/',
                'storage': 'https://www.dns-shop.ru/catalog/17a8a01cd1644e77/ssd-nakopiteli/'
            }
            
            if category not in category_urls:
                return
                
            self.driver.get(category_urls[category])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-item"))
            )
            
            items = self.driver.find_elements(By.CLASS_NAME, "product-item")
            for item in items[:10]:  # Берем первые 10 товаров
                try:
                    title = item.find_element(By.CLASS_NAME, "product-item__title").text
                    price = int(item.find_element(By.CLASS_NAME, "product-item__price").text.replace(" ", "").replace("₽", ""))
                    url = item.find_element(By.CLASS_NAME, "product-item__title").get_attribute("href")
                    
                    self.components.append({
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'DNS',
                        'category': category,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    print(f"Ошибка при парсинге товара DNS: {e}")
                    continue
                    
        except Exception as e:
            print(f"Ошибка при парсинге DNS: {e}")

    def parse_citilink_components(self, category):
        """Парсинг комплектующих с Citilink"""
        try:
            category_urls = {
                'cpu': 'https://www.citilink.ru/catalog/processory/',
                'gpu': 'https://www.citilink.ru/catalog/videokarty/',
                'motherboard': 'https://www.citilink.ru/catalog/materinskie-platy/',
                'ram': 'https://www.citilink.ru/catalog/operativnaya-pamyat/',
                'storage': 'https://www.citilink.ru/catalog/ssd-nakopiteli/'
            }
            
            if category not in category_urls:
                return
                
            self.driver.get(category_urls[category])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ProductCard"))
            )
            
            items = self.driver.find_elements(By.CLASS_NAME, "ProductCard")
            for item in items[:10]:
                try:
                    title = item.find_element(By.CLASS_NAME, "ProductCard__name").text
                    price = int(item.find_element(By.CLASS_NAME, "ProductCard__price").text.replace(" ", "").replace("₽", ""))
                    url = item.find_element(By.CLASS_NAME, "ProductCard__name").get_attribute("href")
                    
                    self.components.append({
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'Citilink',
                        'category': category,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    print(f"Ошибка при парсинге товара Citilink: {e}")
                    continue
                    
        except Exception as e:
            print(f"Ошибка при парсинге Citilink: {e}")

    def parse_mvideo_components(self, category):
        """Парсинг комплектующих с М.Видео"""
        try:
            category_urls = {
                'cpu': 'https://www.mvideo.ru/kompyutery/komplektuyuschie/processory',
                'gpu': 'https://www.mvideo.ru/kompyutery/komplektuyuschie/videokarty',
                'motherboard': 'https://www.mvideo.ru/kompyutery/komplektuyuschie/materinskie-platy',
                'ram': 'https://www.mvideo.ru/kompyutery/komplektuyuschie/operativnaya-pamyat',
                'storage': 'https://www.mvideo.ru/kompyutery/komplektuyuschie/ssd-nakopiteli'
            }
            
            if category not in category_urls:
                return
                
            self.driver.get(category_urls[category])
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-tile"))
            )
            
            items = self.driver.find_elements(By.CLASS_NAME, "product-tile")
            for item in items[:10]:
                try:
                    title = item.find_element(By.CLASS_NAME, "product-title").text
                    price = int(item.find_element(By.CLASS_NAME, "price").text.replace(" ", "").replace("₽", ""))
                    url = item.find_element(By.CLASS_NAME, "product-title").get_attribute("href")
                    
                    self.components.append({
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'М.Видео',
                        'category': category,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    print(f"Ошибка при парсинге товара М.Видео: {e}")
                    continue
                    
        except Exception as e:
            print(f"Ошибка при парсинге М.Видео: {e}")

    def get_component_by_budget(self, category, budget):
        """Получение комплектующего по бюджету"""
        if not self.components:
            return None
            
        # Фильтруем компоненты по категории и бюджету
        suitable_components = [
            comp for comp in self.components 
            if comp['category'] == category and comp['price'] <= budget
        ]
        
        if not suitable_components:
            return None
            
        # Возвращаем случайный подходящий компонент
        return random.choice(suitable_components)

    def save_data(self):
        """Сохранение данных в CSV и JSON"""
        if not self.components:
            return
            
        df = pd.DataFrame(self.components)
        df.to_csv('components_data.csv', index=False)
        
        with open('components_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.components, f, ensure_ascii=False, indent=2)

    def close(self):
        """Закрытие браузера"""
        self.driver.quit()

    def main(self, category):
        """Основной метод парсинга"""
        try:
            self.parse_dns_components(category)
            self.parse_citilink_components(category)
            self.parse_mvideo_components(category)
            self.save_data()
        finally:
            self.close() 