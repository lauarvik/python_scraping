import requests
from lxml import html
from pprint import pprint

def get_link(l):
  return f'https://{domain}{l[0]}' if l else None


def get_elem(l):
  return l[0] if l else None

domain = 'zakonvremeni.ru'
url = f'https://{domain}/component/listallarticles/'
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}
params = {
  # параметры пока не требуются
  #'page': '1',
}

session = requests.Session()
session.headers.update(headers)

response = session.get(url, params=params)

if response.status_code != 200:
  print('Ошибка:', response.status_code)
  exit(1)

dom = html.fromstring(response.text)
articles = dom.xpath("//article")

data = []
for article in articles:
  news_dict = dict(
    title = get_elem(article.xpath(".//h3/a/text()")),
    link = get_link(article.xpath(".//h3/a/@href")),
    #категории оставим в виде списка, т.к. их две
    #хотя можно было бы разбить на cat1 и cat2
    category = article.xpath(".//div[@class='category']/a/text()"),
    date = get_elem(article.xpath(".//div[@class='date']/text()")),
    content = get_elem(article.xpath(".//div[@class='content']/text()")),
  )
  data += [news_dict]

pprint(data)
print(f'Обработано {len(data)} новостей')
