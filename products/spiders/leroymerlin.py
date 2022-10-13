import re
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import HtmlResponse
from products.items import ProductsItem, ProductsLoader
from urllib.parse import urlparse

class LeroymerlinSpider(CrawlSpider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    
    #для перехвата ответов защиты QRATOR
    handle_httpstatus_list = [401]

    custom_settings = {
        'DOWNLOAD_DELAY': 1.25,
        'CONCURRENT_REQUESTS':  4,
        'LOG_LEVEL_OTHERS': 'WARNING',
    }

    rules = (
        Rule(LinkExtractor(allow=r'page=\d+$')),
        Rule(LinkExtractor(allow=r'/product/.+-\d+/$'), callback='parse_item', follow=True),
    )

    def __init__(self, *a, **kw):
        q = kw.get('q', 'удиви меня')
        self.start_urls = [f'https://leroymerlin.ru/search/?q={q}&page=1']
        print(kw)
        super().__init__(*a, **kw)

    def handle_401_error(self, response:HtmlResponse):
        #чтобы не импортировать значение cookie qrator_jsid из браузера (для обхода защиты CSRF от QRATOR) попробуем получить её самостоятельно
        import requests
        if cookie := response.headers.get('Set-Cookie'):
            if match := re.search(r'qrator_jsr=((\d+\.\d+)\..+?)-(.+?)-', cookie.decode('utf-8')):
                nonce, ts, qsessid = match.groups()
                self.logger.info('Подбор знаничения pow')
                session = requests.Session()
                pow = 0
                p = urlparse(response.url)
                status = 403
                while status == 403 and pow < 1024:
                    if not pow % 10:
                        print('.', end='', flush=True)
                    pow += 1
                    url = f'{p.scheme}://{p.netloc}/__qrator/validate?pow={pow}&nonce={nonce}&qsessid={qsessid}'
                    r = session.post(url, json={}, verify=True)
                    if (status := r.status_code) == 200: break
                else:
                    self.logger.error(f'Перебор pow завершился ничем. status: {status}')
                    return
                print()
                cookie = r.headers.get('Set-Cookie')
                if match := re.search(r'(qrator_jsid)=(.+)$', str(cookie)):
                    _, qrator_jsid = match.groups()
                    self.logger.info(f'Значение найдено: pow={pow}, qrator_jsid={qrator_jsid}')
                    return Request(response.url, cookies={'qrator_jsid': qrator_jsid})
        
        self.logger.error('Что-то пошло не так, кука qrator_jsid не найдена.')
    
    def parse_start_url(self, response:HtmlResponse, **kwargs):
        if response.status == 401:
            return self.handle_401_error(response)
        #return response

    def parse_item(self, response:HtmlResponse):
        if response.status == 401:
            self.logger.info('Неожиданное появление кода 401, попробуем переинициализировать QRATOR')
            return self.handle_401_error(response)
        loader = ProductsLoader(item=ProductsItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_css('name', 'h1 ::text')
        loader.add_css('price', 'span[slot="price"]::text')
        loader.add_css('images', 'picture[slot] img::attr(src)')
        loader.add_css('characteristics','#characteristics dl ::text')

        return loader.load_item()

