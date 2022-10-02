# * Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой
# больше введённой суммы (необходимо анализировать оба поля зарплаты).
from datetime import datetime
import requests
import xmltodict
from pymongo import MongoClient
from pprint import pprint

#для простоты нет проверок на ошибки

def get_exchange_rate():
  resp = requests.get('https://www.cbr.ru/scripts/XML_daily.asp?date_req=' + datetime.now().strftime('%d/%m/%Y'))
  curr = xmltodict.parse(resp.text)
  valuta = {}
  for i in curr['ValCurs']['Valute']:
    valuta[i['CharCode']] = float(i['Value'].replace(',', '.'))
  return valuta


#заполняем словарь, сконвертировав рубли во все валюты, присутствующие в бвзе
def fill_salary_dict(target, coll):
  result = {}
  currency_set = set()
  ex_r = get_exchange_rate()
  for i in coll.find({'salary_currency': {'$nin': ['руб', None]}}):
    currency_set.add(i['salary_currency'])
  result['руб'] = target
  for i in currency_set:
    result[i]  = round(target / ex_r[i], 2)
  return result


def find_salary_greater_than(target, coll):
  salary_dict = fill_salary_dict(target_salary, coll)
  print('Искомая з/п в валютах базы: ', salary_dict)
  print('Найденные вакансии: ')
  for currency, salary in salary_dict.items():
    request = {'$and': [{'salary_currency': currency}, {'$or': [{'salary_min': {'$gt': salary}}, {'salary_max': {'$gt': salary}}]}]}
    for result in coll.find(request):
      pprint(result)

coll = MongoClient().jobs.vacancies

#искомая зарплата в рублях
target_salary = 360000
find_salary_greater_than(target_salary, coll)
