import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import pandas as pd
import json
from datetime import datetime, timedelta
import random
import time
import re
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional
import hashlib
import undetected_chromedriver as uc
from fake_useragent import UserAgent

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

class ComponentsParser:
    def __init__(self):
        self.components = {
            'cpu': [],
            'gpu': [],
            'motherboard': [],
            'ram': [],
            'storage': []
        }
        self.ua = UserAgent()
        self.cache_dir = "cache"
        self.cache_ttl = 3600  # 1 час
        self.driver = None
        self.proxies = self.load_proxies()
        self.last_update = None
        self.update_interval = timedelta(hours=1)
        
        # Создаем директорию для кэша, если её нет
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        logger.info("Инициализация парсера комплектующих...")
        self.load_data()
        logger.info("Парсер комплектующих инициализирован")

    def needs_update(self) -> bool:
        """Проверяет, нужно ли обновить данные"""
        if self.last_update is None:
            return True
        return datetime.now() - self.last_update > self.update_interval

    def load_proxies(self) -> List[str]:
        """Загрузка списка прокси"""
        try:
            response = requests.get('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt')
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                logger.info(f"Загружено {len(proxies)} прокси")
                return proxies
            return []
        except Exception as e:
            logger.error(f"Ошибка при загрузке прокси: {str(e)}")
            return []

    def get_random_proxy(self) -> Optional[str]:
        """Получение случайного прокси"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def setup_driver(self):
        """Настройка драйвера Chrome"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={self.get_random_user_agent()}')
            
            proxy = self.get_random_proxy()
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            
            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            logger.info("Драйвер успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации драйвера: {str(e)}")
            raise

    def close_driver(self):
        """Закрытие драйвера"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка при закрытии драйвера: {str(e)}")
            finally:
                self.driver = None

    def get_cache_key(self, url: str) -> str:
        """Получение ключа кэша для URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def get_cached_data(self, url: str) -> Optional[Dict]:
        """Получение данных из кэша"""
        try:
            cache_key = self.get_cache_key(url)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            if os.path.exists(cache_file):
                file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                if datetime.now() - file_time < timedelta(seconds=self.cache_ttl):
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Ошибка при чтении кэша: {str(e)}")
            return None

    def save_to_cache(self, url: str, data: Dict):
        """Сохранение данных в кэш"""
        try:
            cache_key = self.get_cache_key(url)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка при сохранении в кэш: {str(e)}")

    def parse_dns(self, category: str):
        """Парсинг DNS"""
        try:
            if not self.needs_update():
                return
                
            logger.info(f"Начинаем парсинг DNS для категории {category}...")
            self.setup_driver()
            
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
            time.sleep(random.uniform(2, 4))
            
            # Ждем загрузки элементов
            wait = WebDriverWait(self.driver, 20)
            items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'catalog-product')))
            
            logger.info(f"Найдено товаров на DNS: {len(items)}")
            
            for item in items:
                try:
                    title = item.find_element(By.CLASS_NAME, 'catalog-product__name').text.strip()
                    price = item.find_element(By.CLASS_NAME, 'product-buy__price').text.strip()
                    url = item.find_element(By.CLASS_NAME, 'catalog-product__name').get_attribute('href')
                    
                    # Очищаем цену от символов
                    price = int(re.sub(r'[^\d]', '', price))
                    
                    component_data = {
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'DNS',
                        'category': category,
                        'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.components[category].append(component_data)
                    logger.info(f"Добавлен товар: {title} - {price} руб.")
                except Exception as e:
                    logger.error(f"Ошибка при парсинге товара DNS: {str(e)}")
                    continue
            
            self.last_update = datetime.now()
            logger.info(f"Парсинг DNS для категории {category} завершен")
        except Exception as e:
            logger.error(f"Ошибка при парсинге DNS: {str(e)}")
        finally:
            self.close_driver()

    def parse_citilink(self, category: str):
        """Парсинг Citilink"""
        try:
            if not self.needs_update():
                return
                
            logger.info(f"Начинаем парсинг Citilink для категории {category}...")
            self.setup_driver()
            
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
            time.sleep(random.uniform(2, 4))
            
            # Ждем загрузки элементов
            wait = WebDriverWait(self.driver, 20)
            items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ProductCard')))
            
            logger.info(f"Найдено товаров на Citilink: {len(items)}")
            
            for item in items:
                try:
                    title = item.find_element(By.CLASS_NAME, 'ProductCard__name').text.strip()
                    price = item.find_element(By.CLASS_NAME, 'ProductCard__price_current_price').text.strip()
                    url = item.find_element(By.CLASS_NAME, 'ProductCard__name').get_attribute('href')
                    
                    # Очищаем цену от символов
                    price = int(re.sub(r'[^\d]', '', price))
                    
                    component_data = {
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'Citilink',
                        'category': category,
                        'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.components[category].append(component_data)
                    logger.info(f"Добавлен товар: {title} - {price} руб.")
                except Exception as e:
                    logger.error(f"Ошибка при парсинге товара Citilink: {str(e)}")
                    continue
            
            self.last_update = datetime.now()
            logger.info(f"Парсинг Citilink для категории {category} завершен")
        except Exception as e:
            logger.error(f"Ошибка при парсинге Citilink: {str(e)}")
        finally:
            self.close_driver()

    def parse_mvideo(self, category: str):
        """Парсинг М.Видео"""
        try:
            if not self.needs_update():
                return
                
            logger.info(f"Начинаем парсинг М.Видео для категории {category}...")
            self.setup_driver()
            
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
            time.sleep(random.uniform(2, 4))
            
            # Ждем загрузки элементов
            wait = WebDriverWait(self.driver, 20)
            items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-grid__item')))
            
            logger.info(f"Найдено товаров на М.Видео: {len(items)}")
            
            for item in items:
                try:
                    title = item.find_element(By.CLASS_NAME, 'product-title__text').text.strip()
                    price = item.find_element(By.CLASS_NAME, 'price__main-value').text.strip()
                    url = item.find_element(By.CLASS_NAME, 'product-title__text').get_attribute('href')
                    
                    # Очищаем цену от символов
                    price = int(re.sub(r'[^\d]', '', price))
                    
                    component_data = {
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'М.Видео',
                        'category': category,
                        'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.components[category].append(component_data)
                    logger.info(f"Добавлен товар: {title} - {price} руб.")
                except Exception as e:
                    logger.error(f"Ошибка при парсинге товара М.Видео: {str(e)}")
                    continue
            
            self.last_update = datetime.now()
            logger.info(f"Парсинг М.Видео для категории {category} завершен")
        except Exception as e:
            logger.error(f"Ошибка при парсинге М.Видео: {str(e)}")
        finally:
            self.close_driver()

    def update_data(self):
        """Обновление данных"""
        try:
            if not self.needs_update():
                return
                
            logger.info("Начинаем обновление данных...")
            
            # Парсим для каждой категории
            for category in self.components.keys():
                self.parse_dns(category)
                time.sleep(random.uniform(2, 4))
                
                self.parse_citilink(category)
                time.sleep(random.uniform(2, 4))
                
                self.parse_mvideo(category)
                time.sleep(random.uniform(2, 4))
            
            self.last_update = datetime.now()
            logger.info("Обновление данных завершено")
            
            # Сохраняем обновленные данные
            self.save_to_json()
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных: {str(e)}")

    def get_component_by_budget(self, category: str, budget: int) -> Optional[Dict]:
        """Получение комплектующего по бюджету"""
        try:
            if not self.components.get(category):
                logger.warning(f"Нет доступных комплектующих категории {category}")
                return None
                
            suitable_components = [
                comp for comp in self.components[category]
                if comp['price'] <= budget
            ]
            
            if not suitable_components:
                logger.warning(f"Не найдено подходящих комплектующих для бюджета {budget}")
                return None
                
            component = random.choice(suitable_components)
            logger.info(f"Найдено подходящее комплектующее: {component['title']}")
            return component
            
        except Exception as e:
            logger.error(f"Ошибка при получении комплектующего: {str(e)}")
            return None

    def close(self):
        """Закрытие парсера"""
        self.close_driver()
        logger.info("Парсер комплектующих закрыт")

    def get_random_user_agent(self):
        """Получение случайного User-Agent"""
        try:
            return self.ua.random
        except Exception as e:
            logger.error(f"Ошибка при получении User-Agent: {str(e)}")
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def get_headers(self):
        """Получение заголовков для запросов"""
        return {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
        }

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
                    
                    self.components[category].append({
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
                    
                    self.components[category].append({
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
                    
                    self.components[category].append({
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

    def save_data(self):
        """Сохранение данных в CSV и JSON"""
        if not self.components:
            return
            
        df = pd.DataFrame(self.components)
        df.to_csv('components_data.csv', index=False)
        
        with open('components_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.components, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """Загрузка данных из кэша"""
        try:
            with open('components_data.json', 'r', encoding='utf-8') as f:
                self.components = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {str(e)}")

    def save_to_json(self):
        """Сохранение данных в JSON"""
        try:
            with open('components_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.components, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных: {str(e)}")

    def main(self, category):
        """Основной метод парсинга"""
        try:
            self.parse_dns_components(category)
            self.parse_citilink_components(category)
            self.parse_mvideo_components(category)
            self.save_data()
        finally:
            self.close() 