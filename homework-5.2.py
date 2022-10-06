# Написать программу, которая собирает товары «В тренде» с сайта техники mvideo и складывает данные в БД.

from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os, time, re

def format_price(price):
    return int(re.sub(r'\D', '', price))

def store_good_to_db(doc, collection):
    #добавляем новые, обновялем старые (upsert=True)
    collection.update_one({'link': doc['link']}, {'$set': doc}, upsert=True)

#подключаемся к базе данных
goods_collection = MongoClient().mvideo.goods

options = Options()
options.add_argument('start-maximized')
#директория, где находится текущий скрипт
curdir = os.path.dirname(os.path.abspath(__file__))
#используем executable_path вместо Service, чтобы программа работала и с 3й и с 4й версией selenium
driver = webdriver.Chrome(executable_path=os.path.join(curdir, "chromedriver.exe"), options=options)
driver.implicitly_wait(1)

driver.get('https://www.mvideo.ru/')

max_errors = 10
#элемент html используется для отправки нажатия клавиш
html = driver.find_element(By.TAG_NAME, 'html')
while max_errors:
    try:
        #Ищем кнопку "В тренде"
        elem = driver.find_element(By.XPATH, '//button[.//span[contains(text(), "В тренде")]]')
        elem.click()
        break
    #если не нашли, то жмём PageDown
    except NoSuchElementException as e:
        html.send_keys(Keys.PAGE_DOWN)
        time.sleep(3)
    except Exception as e:
        print(type(e))
    max_errors -= 1
else:
    print('Превышен лимит ошибок.')
    driver.quit()
    exit(1)

print('Ищем товары...')
try:
    goods = driver.find_element(By.XPATH, '//mvid-product-cards-group[@_ngcontent-serverapp-c273]')
except NoSuchElementException as e:
    print('Группа товаров не найдена.')
    driver.quit()
    exit(1)

for good in zip(
    goods.find_elements(By.XPATH, './div[contains(@class, "product-mini-card__name")]'),
    goods.find_elements(By.XPATH, './div[contains(@class, "product-mini-card__price")]')
):
    doc = dict(
        name = good[0].text, 
        price = format_price(good[1].find_element(By.XPATH, './/span[@class="price__main-value"]').text), 
        link = good[0].find_element(By.XPATH, './/a').get_attribute('href')
    )
    #print(doc['link'])
    print(f'{doc["name"]}: {doc["price"]} руб.')
    store_good_to_db(doc, goods_collection)
    
driver.quit()
