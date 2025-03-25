import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime
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
        print("Инициализация парсера...")
        self.load_data()
        print(f"Всего сборок после инициализации: {len(self.pc_builds)}")

    def load_proxies(self) -> List[str]:
        """Загрузка списка прокси"""
        try:
            # Получаем бесплатные прокси
            response = requests.get('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt')
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                print(f"Загружено {len(proxies)} прокси")
                return proxies
        except Exception as e:
            print(f"Ошибка при загрузке прокси: {e}")
        return []

    def get_random_proxy(self) -> Optional[str]:
        """Получение случайного прокси"""
        if self.proxies:
            return random.choice(self.proxies)
        return None

    def setup_driver(self):
        """Настройка undetected-chromedriver"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Добавляем случайный прокси
            proxy = self.get_random_proxy()
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            
            # Добавляем случайный User-Agent
            options.add_argument(f'user-agent={self.ua.random}')
            
            # Создаем драйвер с дополнительными параметрами
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=None,
                browser_executable_path=None,
                suppress_welcome=True,
                use_subprocess=True
            )
            
            # Устанавливаем таймаут
            self.driver.set_page_load_timeout(30)
            
            # Добавляем скрипты для обхода обнаружения
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.ua.random})
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("Драйвер успешно настроен")
        except Exception as e:
            print(f"Ошибка при настройке драйвера: {e}")
            raise

    def close_driver(self):
        """Закрытие драйвера"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Ошибка при закрытии драйвера: {e}")
            finally:
                self.driver = None

    def get_cache_key(self, url: str) -> str:
        """Создание уникального ключа кэша для URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def get_cached_data(self, url: str) -> Optional[Dict]:
        """Получение данных из кэша"""
        cache_key = self.get_cache_key(url)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            file_time = os.path.getmtime(cache_file)
            if time.time() - file_time < self.cache_ttl:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Ошибка чтения кэша: {e}")
        return None

    def save_to_cache(self, url: str, data: Dict):
        """Сохранение данных в кэш"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        cache_key = self.get_cache_key(url)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения в кэш: {e}")

    async def fetch_mobile_api(self, url: str) -> Optional[str]:
        """Получение данных через мобильное API"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': url,
            'Origin': url.split('/')[2],
            'Connection': 'keep-alive'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.error(f"Ошибка API: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка запроса: {e}")
            return None

    def parse_dns(self):
        """Парсинг сборок ПК с DNS"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.driver:
                    self.setup_driver()
                
                url = "https://www.dns-shop.ru/catalog/17a8a01d16404e77/sborki-pk/"
                print(f"Парсинг DNS (попытка {retry_count + 1}/{max_retries})...")
                
                self.driver.get(url)
                time.sleep(random.uniform(3, 5))
                
                # Ждем загрузки элементов с увеличенным таймаутом
                wait = WebDriverWait(self.driver, 20)
                builds = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'catalog-product')))
                
                print(f"Найдено сборок на DNS: {len(builds)}")
                
                for build in builds:
                    try:
                        title = build.find_element(By.CLASS_NAME, 'catalog-product__name').text.strip()
                        price = build.find_element(By.CLASS_NAME, 'product-buy__price').text.strip()
                        url = build.find_element(By.CLASS_NAME, 'catalog-product__name').get_attribute('href')
                        
                        build_type = 'pc'
                        purpose = 'gaming' if 'игровой' in title.lower() else 'work'
                        
                        print(f"Найдена сборка: {title} - {price}")
                        
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
                    except Exception as e:
                        print(f"Ошибка при парсинге сборки DNS: {e}")
                        continue
                
                break  # Если успешно, выходим из цикла
                
            except TimeoutException:
                print(f"Таймаут при парсинге DNS (попытка {retry_count + 1})")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            except WebDriverException as e:
                print(f"Ошибка WebDriver при парсинге DNS: {e}")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"Неожиданная ошибка при парсинге DNS: {e}")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            finally:
                self.close_driver()

    def parse_citilink(self):
        """Парсинг сборок ПК с Ситилинк"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.driver:
                    self.setup_driver()
                
                url = "https://www.citilink.ru/catalog/sborki-pk/"
                print(f"Парсинг Ситилинк (попытка {retry_count + 1}/{max_retries})...")
                
                self.driver.get(url)
                time.sleep(random.uniform(3, 5))
                
                # Ждем загрузки элементов с увеличенным таймаутом
                wait = WebDriverWait(self.driver, 20)
                builds = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product_data__gtm-js')))
                
                print(f"Найдено сборок на Ситилинк: {len(builds)}")
                
                for build in builds:
                    try:
                        title = build.find_element(By.CLASS_NAME, 'ProductCardHorizontal__title').text.strip()
                        price = build.find_element(By.CLASS_NAME, 'ProductCardHorizontal__price_current_price').text.strip()
                        url = build.find_element(By.CLASS_NAME, 'ProductCardHorizontal__title').get_attribute('href')
                        
                        build_type = 'pc'
                        purpose = 'gaming' if 'игровой' in title.lower() else 'work'
                        
                        print(f"Найдена сборка: {title} - {price}")
                        
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
                    except Exception as e:
                        print(f"Ошибка при парсинге сборки Ситилинк: {e}")
                        continue
                
                break  # Если успешно, выходим из цикла
                
            except TimeoutException:
                print(f"Таймаут при парсинге Ситилинк (попытка {retry_count + 1})")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            except WebDriverException as e:
                print(f"Ошибка WebDriver при парсинге Ситилинк: {e}")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"Неожиданная ошибка при парсинге Ситилинк: {e}")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            finally:
                self.close_driver()

    def parse_mvideo(self):
        """Парсинг сборок ПК с М.Видео"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.driver:
                    self.setup_driver()
                
                url = "https://www.mvideo.ru/kompyutery/sborki-pk-118"
                print(f"Парсинг М.Видео (попытка {retry_count + 1}/{max_retries})...")
                
                self.driver.get(url)
                time.sleep(random.uniform(3, 5))
                
                # Ждем загрузки элементов с увеличенным таймаутом
                wait = WebDriverWait(self.driver, 20)
                builds = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-grid__item')))
                
                print(f"Найдено сборок на М.Видео: {len(builds)}")
                
                for build in builds:
                    try:
                        title = build.find_element(By.CLASS_NAME, 'product-title__text').text.strip()
                        price = build.find_element(By.CLASS_NAME, 'price__main-value').text.strip()
                        url = build.find_element(By.CLASS_NAME, 'product-title__text').get_attribute('href')
                        
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
                
                break  # Если успешно, выходим из цикла
                
            except TimeoutException:
                print(f"Таймаут при парсинге М.Видео (попытка {retry_count + 1})")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            except WebDriverException as e:
                print(f"Ошибка WebDriver при парсинге М.Видео: {e}")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"Неожиданная ошибка при парсинге М.Видео: {e}")
                retry_count += 1
                self.close_driver()
                time.sleep(random.uniform(5, 10))
            finally:
                self.close_driver()

    def update_data(self):
        """Обновление данных с сайтов"""
        print("Начинаем обновление данных...")
        try:
            # Сохраняем старые данные
            old_builds = self.pc_builds.copy()
            
            # Очищаем список и добавляем тестовые данные
            self.pc_builds = []
            self.add_test_data()
            
            # Парсим сайты последовательно
            self.parse_dns()
            time.sleep(random.uniform(2, 4))
            
            self.parse_citilink()
            time.sleep(random.uniform(2, 4))
            
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

    def close(self):
        """Закрытие парсера и сохранение данных"""
        try:
            self.save_to_json()
            print("Данные сохранены")
        except Exception as e:
            print(f"Ошибка при закрытии парсера: {e}")

    def get_random_user_agent(self):
        """Получение случайного User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)

    def get_headers(self):
        """Получение заголовков для запроса"""
        return {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
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