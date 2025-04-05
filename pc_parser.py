import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import random
import re
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
from fake_useragent import UserAgent
import logging
from typing import Dict, List, Optional
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

class PCParser:
    def __init__(self):
        self.pc_builds = []
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
            
        logger.info("Инициализация парсера...")
        self.load_data()
        logger.info(f"Всего сборок после инициализации: {len(self.pc_builds)}")

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
        """Настройка веб-драйвера"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={UserAgent().random}')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": UserAgent().random
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Веб-драйвер успешно настроен")
        except Exception as e:
            logger.error(f"Ошибка при настройке веб-драйвера: {str(e)}")
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

    async def fetch_mobile_api(self, url: str) -> Optional[str]:
        """Получение данных через мобильное API"""
        try:
            headers = self.get_headers()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
                        return None
        except Exception as e:
            logger.error(f"Ошибка при запросе к API: {str(e)}")
            return None

    def parse_dns(self):
        """Парсинг готовых сборок с DNS"""
        try:
            if not self.needs_update():
                return
            
            logger.info("Начинаем парсинг готовых сборок DNS...")
                    self.setup_driver()
                
            # URL для готовых сборок
                url = "https://www.dns-shop.ru/catalog/17a8a01d16404e77/sborki-pk/"
                self.driver.get(url)
            time.sleep(random.uniform(2, 4))
                
            # Ждем загрузки элементов
                wait = WebDriverWait(self.driver, 20)
            
            # Получаем список сборок
            builds = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product-card')))
                
            logger.info(f"Найдено сборок на DNS: {len(builds)}")
                
                for build in builds:
                    try:
                    # Получаем название сборки
                    title = build.find_element(By.CSS_SELECTOR, '.product-card__title').text.strip()
                    
                    # Получаем цену
                    price_element = build.find_element(By.CSS_SELECTOR, '.product-card__price')
                    price = int(''.join(filter(str.isdigit, price_element.text)))
                    
                    # Получаем ссылку
                    url = build.find_element(By.CSS_SELECTOR, 'a.product-card__link').get_attribute('href')
                    
                    # Определяем тип и назначение
                        build_type = 'pc'
                        purpose = 'gaming' if 'игровой' in title.lower() else 'work'
                        
                        build_data = {
                            'title': title,
                            'price': price,
                            'url': url,
                            'source': 'DNS',
                            'type': build_type,
                            'purpose': purpose,
                            'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    
                        self.pc_builds.append(build_data)
                    logger.info(f"Добавлена сборка: {title} - {price} руб.")
                    
                    except Exception as e:
                    logger.error(f"Ошибка при парсинге сборки DNS: {str(e)}")
                        continue
                
            self.last_update = datetime.now()
            logger.info("Парсинг DNS завершен")
            
            except Exception as e:
            logger.error(f"Ошибка при парсинге DNS: {str(e)}")
            finally:
                self.close_driver()

    def parse_citilink(self):
        """Парсинг Citilink"""
        try:
            if not self.needs_update():
                return
                
            logger.info("Начинаем парсинг Citilink...")
            self.setup_driver()
                
                url = "https://www.citilink.ru/catalog/sborki-pk/"
                self.driver.get(url)
            time.sleep(random.uniform(2, 4))
                
            # Ждем загрузки элементов
                wait = WebDriverWait(self.driver, 20)
                builds = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product_data__gtm-js')))
                
            logger.info(f"Найдено сборок на Citilink: {len(builds)}")
                
                for build in builds:
                    try:
                        title = build.find_element(By.CLASS_NAME, 'ProductCardHorizontal__title').text.strip()
                        price = build.find_element(By.CLASS_NAME, 'ProductCardHorizontal__price_current_price').text.strip()
                        url = build.find_element(By.CLASS_NAME, 'ProductCardHorizontal__title').get_attribute('href')
                        
                    # Определяем тип и назначение
                        build_type = 'pc'
                        purpose = 'gaming' if 'игровой' in title.lower() else 'work'
                        
                    # Очищаем цену от символов
                    price = int(re.sub(r'[^\d]', '', price))
                        
                        build_data = {
                            'title': title,
                            'price': price,
                            'url': url,
                            'source': 'Ситилинк',
                            'type': build_type,
                            'purpose': purpose,
                            'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        self.pc_builds.append(build_data)
                    logger.info(f"Добавлена сборка: {title} - {price} руб.")
                    except Exception as e:
                    logger.error(f"Ошибка при парсинге сборки Citilink: {str(e)}")
                        continue
                
            self.last_update = datetime.now()
            logger.info("Парсинг Citilink завершен")
            except Exception as e:
            logger.error(f"Ошибка при парсинге Citilink: {str(e)}")
            finally:
                self.close_driver()

    def parse_mvideo(self):
        """Парсинг М.Видео"""
        try:
            if not self.needs_update():
                return
                
            logger.info("Начинаем парсинг М.Видео...")
            self.setup_driver()
                
                url = "https://www.mvideo.ru/kompyutery/sborki-pk-118"
                self.driver.get(url)
            time.sleep(random.uniform(2, 4))
                
            # Ждем загрузки элементов
                wait = WebDriverWait(self.driver, 20)
                builds = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-grid__item')))
                
            logger.info(f"Найдено сборок на М.Видео: {len(builds)}")
                
                for build in builds:
                    try:
                        title = build.find_element(By.CLASS_NAME, 'product-title__text').text.strip()
                        price = build.find_element(By.CLASS_NAME, 'price__main-value').text.strip()
                        url = build.find_element(By.CLASS_NAME, 'product-title__text').get_attribute('href')
                        
                    # Определяем тип и назначение
                    build_type = 'pc'
                    purpose = 'gaming' if 'игровой' in title.lower() else 'work'
                    
                    # Очищаем цену от символов
                    price = int(re.sub(r'[^\d]', '', price))
                        
                        build_data = {
                            'title': title,
                            'price': price,
                            'url': url,
                            'source': 'М.Видео',
                        'type': build_type,
                        'purpose': purpose,
                            'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        self.pc_builds.append(build_data)
                    logger.info(f"Добавлена сборка: {title} - {price} руб.")
                    except Exception as e:
                    logger.error(f"Ошибка при парсинге сборки М.Видео: {str(e)}")
                        continue
                
            self.last_update = datetime.now()
            logger.info("Парсинг М.Видео завершен")
            except Exception as e:
            logger.error(f"Ошибка при парсинге М.Видео: {str(e)}")
            finally:
                self.close_driver()

    def parse_dns_configurator(self):
        """Простой и надежный парсинг сборок с DNS Configurator"""
        try:
            logger.info("Начинаем парсинг DNS Configurator...")
            self.setup_driver()
            
            # Переходим на страницу конфигуратора
            self.driver.get("https://www.dns-shop.ru/configurator/")
            time.sleep(3)
            
            # Находим кнопку "Лучшие пользовательские сборки ПК" и заходим в этот раздел
            try:
                logger.info("Ищем раздел с популярными сборками...")
                self.driver.execute_script("document.querySelector('.configurator-content__assemblies-list-title').scrollIntoView()")
                time.sleep(1)
                
                # Получаем список пользовательских сборок
                logger.info("Получаем список пользовательских сборок...")
                configs = self.driver.find_elements(By.CSS_SELECTOR, "div[data-role='group-configuration']")
                logger.info(f"Найдено {len(configs)} сборок")
                
                if not configs:
                    logger.warning("Сборки не найдены, пробуем альтернативный путь")
                    # Альтернативный путь - ищем кнопку для просмотра готовых сборок
                    view_all_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-role='configurator-content__assemblies-list-to-catalog-btn']")
                    if view_all_btn:
                        logger.info("Нажимаем кнопку для просмотра готовых сборок")
                        view_all_btn.click()
                        time.sleep(3)
                        configs = self.driver.find_elements(By.CSS_SELECTOR, "div[data-role='group-configuration']")
                        logger.info(f"Найдено {len(configs)} сборок через альтернативный путь")
                
                # Обрабатываем каждую сборку
                for config in configs:
                    try:
                        # Получаем GUID конфигурации для формирования ссылки
                        guid = config.get_attribute("data-configuration-guid")
                        if not guid:
                            continue
                        
                        # Формируем ссылку на конфигурацию
                        config_url = f"https://www.dns-shop.ru/configurator/user-pc/configuration/{guid}/"
                        
                        # Получаем компоненты в этой конфигурации
                        components = config.find_elements(By.CSS_SELECTOR, ".assembly-item__list-product")
                        component_list = []
                        
                        # Получаем общую стоимость
                        total_price = 0
                        price_elements = config.find_elements(By.CSS_SELECTOR, ".product-buy__price")
                        for price_el in price_elements:
                            try:
                                price_text = price_el.text.strip()
                                price = int(''.join(filter(str.isdigit, price_text)))
                                total_price += price
                            except:
                                pass
                        
                        # Получаем список компонентов
                        for component in components:
                            try:
                                comp_text = component.text.strip()
                                if comp_text:
                                    component_list.append(comp_text)
                            except:
                                pass
                        
                        # Если нашли компоненты, добавляем сборку
                        if component_list:
                            title = f"Сборка DNS: {component_list[0] if component_list else 'Конфигурация'}"
                            
                            build_data = {
                                'title': title, 
                                'price': total_price,
                                'url': config_url,
                                'source': 'DNS Configurator',
                                'components': component_list,
                                'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            self.pc_builds.append(build_data)
                            logger.info(f"Добавлена сборка: {title} - {total_price} руб.")
                    except Exception as e:
                        logger.error(f"Ошибка при парсинге отдельной конфигурации: {str(e)}")
                        continue
            except Exception as e:
                logger.error(f"Ошибка при получении пользовательских сборок: {str(e)}")
            
            # Если не нашли готовых сборок, добавим тестовые данные
            if not self.pc_builds:
                logger.warning("Не удалось найти сборки, добавляем тестовые данные")
                self.add_test_data()
            
            # Сохраняем результат
            self.last_update = datetime.now()
            logger.info(f"Парсинг DNS Configurator завершен. Всего сборок: {len(self.pc_builds)}")
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге DNS Configurator: {str(e)}")
            # Добавляем тестовые данные в случае ошибки
            self.add_test_data()
        finally:
            self.close_driver()

    def get_random_build(self, budget: int) -> Optional[Dict]:
        """Получение случайной сборки по бюджету"""
        try:
            if not self.pc_builds:
                logger.warning("Нет доступных сборок")
                return None
                
            suitable_builds = [
                build for build in self.pc_builds
                if build['price'] <= budget
            ]
            
            if not suitable_builds:
                logger.warning(f"Не найдено подходящих сборок для бюджета {budget}")
                return None
                
            build = random.choice(suitable_builds)
            logger.info(f"Найдена подходящая сборка: {build['title']}")
            return build
            
        except Exception as e:
            logger.error(f"Ошибка при получении случайной сборки: {str(e)}")
            return None

    def close(self):
        """Закрытие парсера"""
        self.close_driver()
        logger.info("Парсер закрыт")

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

    def parse_regard(self):
        """Парсинг сборок ПК с Regard.ru"""
        try:
            url = "https://www.regard.ru/catalog/group4000.htm"
            print("Парсинг Regard.ru...")
            
            # Добавляем случайную задержку
            time.sleep(random.uniform(2, 5))
            
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
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

    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists('pc_builds.json'):
            with open('pc_builds.json', 'r', encoding='utf-8') as f:
                self.pc_builds = json.load(f)
                    logger.info(f"Загружено {len(self.pc_builds)} сборок из файла")
            else:
                logger.info("Файл с данными не найден, добавляем тестовые данные")
            self.add_test_data()
            self.save_to_json()
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {str(e)}")
            logger.info("Добавляем тестовые данные")
            self.add_test_data()
            self.save_to_json()

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

    def save_to_csv(self, filename="pc_builds.csv"):
        """Сохранение данных в CSV файл"""
        df = pd.DataFrame(self.pc_builds)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Данные сохранены в {filename}")

    def save_to_json(self, filename="pc_builds.json"):
        """Сохранение данных в JSON файл"""
        try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.pc_builds, f, ensure_ascii=False, indent=4)
            logger.info(f"Данные сохранены в {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в JSON: {str(e)}")
            logger.exception("Полный стек ошибки:")

    def parse_dns_smart(self):
        """Умный парсинг DNS с созданием оптимальных конфигураций"""
        try:
            logger.info("Запуск умного парсинга DNS...")
            self.setup_driver()
            
            # Переходим на страницу конфигуратора
            url = "https://www.dns-shop.ru/configurator/"
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            # Ждем загрузки элементов
            wait = WebDriverWait(self.driver, 20)
            
            # Категории комплектующих и их селекторы
            categories = {
                'cpu': '[data-category="processor"]',
                'motherboard': '[data-category="motherboard"]',
                'ram': '[data-category="ram"]',
                'gpu': '[data-category="video"]',
                'storage': '[data-category="storage"]',
                'case': '[data-category="case"]',
                'psu': '[data-category="power"]',
                'cooling': '[data-category="cooling"]'
            }
            
            # Бюджетные диапазоны для создания конфигураций
            budget_ranges = [
                {'min': 30000, 'max': 50000, 'type': 'office'},
                {'min': 50000, 'max': 80000, 'type': 'gaming_budget'},
                {'min': 80000, 'max': 120000, 'type': 'gaming_medium'},
                {'min': 120000, 'max': 200000, 'type': 'gaming_high'},
                {'min': 200000, 'max': 500000, 'type': 'workstation'}
            ]
            
            for budget in budget_ranges:
                try:
                    logger.info(f"Создаем конфигурацию для бюджета {budget['min']}-{budget['max']} руб. ({budget['type']})")
                    
                    # Нажимаем кнопку "Начать сборку"
                    start_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.configurator-content__start-button')))
                    start_btn.click()
                    time.sleep(2)
                    
                    components_data = []
                    total_price = 0
                    
                    # Проходим по каждой категории комплектующих
                    for category, selector in categories.items():
                        try:
                            # Открываем категорию
                            category_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            category_btn.click()
                            time.sleep(1)
                            
                            # Ждем загрузки списка компонентов
                            components = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product-buy__price')))
                            
                            # Выбираем компонент в зависимости от бюджета и типа сборки
                            suitable_components = []
                            for comp in components:
                                try:
                                    price_element = comp.find_element(By.CSS_SELECTOR, '.product-buy__price')
                                    price = int(''.join(filter(str.isdigit, price_element.text)))
                                    
                                    # Проверяем, подходит ли компонент по цене
                                    if category == 'cpu':
                                        max_price = budget['max'] * 0.25  # 25% бюджета на процессор
                                    elif category == 'gpu' and 'gaming' in budget['type']:
                                        max_price = budget['max'] * 0.35  # 35% бюджета на видеокарту для игровых сборок
                                    else:
                                        max_price = budget['max'] * 0.15  # 15% бюджета на остальные компоненты
                                    
                                    if price <= max_price:
                                        title = comp.find_element(By.CSS_SELECTOR, '.product-buy__title').text.strip()
                                        suitable_components.append({
                                            'title': title,
                                            'price': price,
                                            'element': comp
                                        })
                                except Exception as e:
                                    continue
                            
                            if suitable_components:
                                # Выбираем оптимальный компонент
                                best_component = max(suitable_components, key=lambda x: x['price'])
                                best_component['element'].click()
                                components_data.append({
                                    'category': category,
                                    'title': best_component['title'],
                                    'price': best_component['price']
                                })
                                total_price += best_component['price']
                                logger.info(f"Добавлен {category}: {best_component['title']} - {best_component['price']} руб.")
                            
                            # Закрываем окно выбора компонентов
                            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.modal-close')))
                            close_btn.click()
                            time.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"Ошибка при выборе {category}: {str(e)}")
                            continue
                    
                    # Сохраняем конфигурацию
                    save_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.configurator-content__save-button')))
                    save_btn.click()
                    time.sleep(2)
                    
                    # Получаем URL сохраненной конфигурации
                    config_url = self.driver.current_url
                    
                    # Формируем название сборки
                    title = f"Оптимальная сборка DNS {budget['type'].replace('_', ' ').title()}"
                    
                    # Сохраняем данные о сборке
                    build_data = {
                        'title': title,
                        'components': components_data,
                        'price': total_price,
                        'url': config_url,
                        'source': 'DNS Smart Config',
                        'budget_range': f"{budget['min']}-{budget['max']}",
                        'type': budget['type'],
                        'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    self.pc_builds.append(build_data)
                    logger.info(f"Создана конфигурация: {title} - {total_price} руб.")
                    
                    # Возвращаемся к начальному экрану конфигуратора
                    self.driver.get(url)
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Ошибка при создании конфигурации {budget['type']}: {str(e)}")
                    continue
            
            self.last_update = datetime.now()
            logger.info("Умный парсинг DNS завершен")
            
        except Exception as e:
            logger.error(f"Ошибка при умном парсинге DNS: {str(e)}")
        finally:
            self.close_driver()

    def update_data(self):
        """Обновление данных"""
        try:
            if not self.needs_update():
                logger.info("Обновление не требуется, данные актуальны")
                return
            
            # Очищаем старые данные перед обновлением
            self.pc_builds = []
            
            logger.info("Начинаем обновление данных...")
            
            # Используем простой парсинг DNS Configurator
            logger.info("Парсинг DNS Configurator...")
            self.parse_dns_configurator()
            
            # Если не удалось получить данные, используем тестовые
            if not self.pc_builds:
                logger.warning("Данные не получены, используем тестовые")
                self.add_test_data()
            
            # Сохраняем обновленные данные
            logger.info(f"Всего сборок: {len(self.pc_builds)}")
            self.save_to_json()
            self.save_to_csv()
            
            self.last_update = datetime.now()
            logger.info("Обновление данных завершено")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных: {str(e)}")
            logger.exception("Полный стек ошибки:")
            # В случае ошибки добавляем тестовые данные
            self.add_test_data()
            self.save_to_json()
            self.save_to_csv()

    def parse_dns_user_config(self, config_url: str):
        """Парсинг пользовательской конфигурации DNS"""
        try:
            logger.info("Начинаем парсинг пользовательской конфигурации DNS...")
            self.setup_driver()
            
            self.driver.get(config_url)
            time.sleep(random.uniform(2, 4))
            
            # Ждем загрузки элементов
            wait = WebDriverWait(self.driver, 20)
            
            # Получаем общую информацию о сборке
            title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.assembly-item__list-created'))).text.strip()
            
            # Получаем список компонентов
            components = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.assembly-item__list-product')))
            
            components_list = []
            total_price = 0
            
            for component in components:
                try:
                    # Название компонента
                    comp_title = component.text.strip()
                    
                    # Цена находится в родительском элементе
                    parent = component.find_element(By.XPATH, '..')  # Переходим к родительскому элементу
                    price_element = parent.find_element(By.CSS_SELECTOR, '.product-buy__price-wrap')
                    if price_element:
                        comp_price = price_element.text.strip()
                        # Извлекаем только цифры из строки с ценой
                        comp_price_int = int(''.join(filter(str.isdigit, comp_price)))
                        total_price += comp_price_int
                        
                        components_list.append({
                            'title': comp_title,
                            'price': comp_price_int
                        })
                        logger.info(f"Добавлен компонент: {comp_title} - {comp_price_int} руб.")
                except Exception as e:
                    logger.error(f"Ошибка при парсинге компонента: {str(e)}")
                    continue
            
            # Формируем данные о сборке
            build_data = {
                'title': title,
                'components': components_list,
                'total_price': total_price,
                'url': config_url,
                'source': 'DNS User Config',
                'type': 'pc',
                'purpose': 'custom',
                'date_parsed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.pc_builds.append(build_data)
            logger.info(f"Добавлена пользовательская сборка: {title} - {total_price} руб.")
            
            return build_data
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге пользовательской конфигурации DNS: {str(e)}")
            return None
        finally:
            self.close_driver()

    def get_build_by_url(self, url: str) -> Optional[Dict]:
        """Получение сборки по URL"""
        try:
            if 'dns-shop.ru/user-pc/configuration/' in url:
                return self.parse_dns_user_config(url)
            
            # Поиск в существующих сборках
            for build in self.pc_builds:
                if build['url'] == url:
                    return build
                
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении сборки по URL: {str(e)}")
            return None

async def main():
    parser = PCParser()
    try:
        print("Начинаем парсинг сборок ПК...")
        await parser.update_data()
        parser.save_to_csv()
        parser.save_to_json()
        parser.close()
        print("Парсинг завершен успешно!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 