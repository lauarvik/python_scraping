from vacancies_grabber import grab_hh_vacancy, grab_superjob_vacancy
from pymongo import MongoClient

def grab_vacations_to_db(query, coll):
  added, updated = 0, 0
  #сбор данных с hh.ru и superjob.ru
  for rec in grab_hh_vacancy(query) + grab_superjob_vacancy(query):
    #используем опцию upsert метода update_one, что позволит исключить дублирование.
    #Обработку исключений, для простоты, опустим.
    if coll.update_one({'link': rec['link']}, {'$set': rec}, upsert=True).upserted_id:
      added += 1
    else:
      updated += 1
  print(f'Добавлено {added} записей')
  print(f'Обновлено {updated} записей')

coll = MongoClient().jobs.vacancies
#coll.drop()
grab_vacations_to_db('python', coll)
