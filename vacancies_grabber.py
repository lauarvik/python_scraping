import requests
import re, csv
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
}

session = requests.Session()
session.headers.update(headers)

def grab_superjob_vacancy(keywords):
  url = 'https://russia.superjob.ru/vacancy/search/'
  page = 1
  vacancies_list = []
  params = {
    'keywords': keywords, # Текст поиска
  }
  while 1:
    if page > 1:
      params['page'] = page
      print(f'.{page}.', end='', flush=True)
    page += 1
    try:
      response = session.get(url, params=params)
    except Exception as e:
      print('Ошибка:', type(e))
      exit(1)

    if response.status_code != 200:
      print('Ошибка:', response.status_code)
      exit(1)

    soup = bs(response.text, features='html.parser')
    divs_list = soup.findAll('div', {'class':'f-test-clickable-'})
    
    #выход из бесконечного цикла
    if not divs_list: break
    for vacancy in divs_list:
      salary_min, salary_max, salary_currency = None, None, None
      name = vacancy.a.get_text()
      employer = vacancy.find('span', {'class': 'f-test-text-vacancy-item-company-name'})
      employer = employer.get_text() if employer else None
      location = vacancy.find('span', {'class': 'f-test-text-company-item-location'})
      location = location.div.div.get_text() if location else None
      link = 'https://superjob.ru' + vacancy.a['href']
      salary = vacancy.find('div', {'class': 'f-test-text-company-item-salary'})
      if salary:
        salary_text = salary.get_text()
        #уничтожаем все пробельные символы
        salary_text = re.sub(r'\s', '', salary_text)
        # число - число валюта
        if match := re.match(r'(\d+)—(\d+)(\w+)', salary_text):
          salary_min, salary_max, salary_currency = match.groups()
        # от число валюта
        elif match := re.match(r'от(\d+)(\w+)', salary_text):
          salary_min, salary_currency = match.groups()
        # до число валюта
        elif match := re.match(r'до(\d+)(\w+)', salary_text):
          salary_max, salary_currency = match.groups()
      vacancy_dict = dict(
        site = 'superjob.ru',
        name = name,
        employer = employer,
        location = location,
        link = link,
        salary_min = salary_min,
        salary_max = salary_max,
        salary_currency = salary_currency,
      )
      vacancies_list.append(vacancy_dict)
  print()
  return vacancies_list


def grab_hh_vacancy(text, area=113, schedule='remote', search_field='name'):
  url = 'https://hh.ru/search/vacancy'
  page = 0
  vacancies_list = []
  params = {
    'area': area, # Регион: Россия (113)
    'schedule': schedule, # График работы: Удаленная работа (remote)
    'search_field': search_field, # Ключевые слова: В названии вакансии (name)
    'text': text, # Текст поиска
    'items_on_page': 20, #Элементов на странице
  }
  while 1:
    if page:
      params['page'] = page
      print(f'.{page}.', end='', flush=True)
    page += 1
    try:
      response = session.get(url, params=params)
    except Exception as e:
      print('Ошибка:', type(e))
      exit(1)

    if response.status_code != 200:
      print('Ошибка:', response.status_code)
      exit(1)

    soup = bs(response.text, features='html.parser')
    divs_list = soup.findAll('div', {'class':'serp-item'})
    #выход из бесконечного цикла
    if not divs_list: break
    
    for vacancy in divs_list:
      name = vacancy.a.get_text()
      employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
      employer = employer.get_text() if employer else None
      location = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-location'})
      location = location.get_text() if location else None
      link = urlparse(vacancy.a['href'])
      link = f'{link.scheme}://{link.hostname}{link.path}'
      salary_min, salary_max, salary_currency = None, None, None
      salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
      if salary:
        salary_text = salary.get_text()
        #уничтожаем все пробельные символы
        salary_text = re.sub(r'\s', '', salary_text)
        # число - число валюта
        if match := re.match(r'(\d+)–(\d+)(\w+)', salary_text):
          salary_min, salary_max, salary_currency = match.groups()
        # от число валюта
        elif match := re.match(r'от(\d+)(\w+)', salary_text):
          salary_min, salary_currency = match.groups()
        # до число валюта
        elif match := re.match(r'до(\d+)(\w+)', salary_text):
          salary_max, salary_currency = match.groups()
      vacancy_dict = dict(
        site = 'hh.ru',
        name = name,
        employer = employer,
        location = location,
        link = link,
        salary_min = salary_min,
        salary_max = salary_max,
        salary_currency = salary_currency,
      )
      vacancies_list.append(vacancy_dict)
  print()
  return vacancies_list

#строка запроса ко всем сайтам
query = 'python'

vacancies_data = []
vdata = grab_hh_vacancy(query)
print(f'Найдено {len(vdata)} вакансий на сайте hh.ru')
vacancies_data += vdata
vdata = grab_superjob_vacancy(query)
vacancies_data += vdata
print(f'Найдено {len(vdata)} вакансий на сайте superjob.ru')
with open('vacancies_data.csv', 'w', encoding='utf-8', newline='') as f:
  columns = ['site', 'name', 'employer', 'location', 'salary_min', 'salary_max', 'salary_currency', 'link']
  writer = csv.DictWriter(f, lineterminator='\n', fieldnames=columns)
  writer.writeheader()
  writer.writerows(vacancies_data)
