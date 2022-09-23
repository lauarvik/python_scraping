import requests
from lxml import html
from pprint import pprint

def get_source(s):
  if not s: return None
  p_data = {
    '#ui-label_moslenta':  'Мослента',
    '#ui-label_secretmag': 'СЕКРЕТ ФИРМЫ',
    '#ui-label_motor':     'motor',
    '#ui-label_ferra':     'Ferra',
  }
  try:
    return p_data[s[0]]
  except KeyError:
    return s[0]

def get_link(ll):
	if not ll: return None
	if ll[0][0] == '/':
	  return f'https://{domain}{ll[0]}' 
	else:
	  return ll[0]

def get_data(data):
  if len(data) == 3:
    return (data[-3] + data[-2], data[-1])
  elif len(data) == 2:
    return (data[-2], data[-1])
  elif len(data) == 1:
    return (data[-1], None)
  else:
    return (None, None)


def get_block(block_class):
  news = dom.xpath(f"//a[contains(@class, '{block_class}')]")
  news_list = []
  for new in news:
    title, time = get_data(new.xpath(".//text()"))
    news_dict = dict(
      title = title,
      link = get_link(new.xpath(".//@href")),
      time = time,
      source = get_source(new.xpath(".//use/@*")),
    )
    news_list.append(news_dict)
  return news_list


domain = 'lenta.ru'
url = f'https://{domain}/'
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}
params = {
# параметры не требуются
}

session = requests.Session()
session.headers.update(headers)

response = session.get(url, params=params)

if response.status_code != 200:
  print('Ошибка:', response.status_code)
  exit(1)

dom = html.fromstring(response.text)

#blocks = ['card-big _slider _partners _extlink', 'card-big _slider _dark _popular _article', 'card-mini _compact', 'card-mini _longgrid', 'card-big _longgrid', 'card-mini _topnews', 'card-big _longgrid', 'card-big _topnews _news']
#чем обрабатывать кучу разных типов блоков по отдельности, рискуя что-то пропустить при изменениях,
#лучше сразу сделать более универсальное решение

blocks = ['card-big', 'card-mini']
data = []
for b in blocks:
  data += get_block(b) 

pprint(data)
print(f'Обработано {len(data)} новостей')
