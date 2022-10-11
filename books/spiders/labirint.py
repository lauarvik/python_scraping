from json import load
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http.response import Response
from books.items import BooksItem, BooksLoader
from itemloaders.processors import MapCompose

class LabirintSpider(CrawlSpider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['http://labirint.ru/books/']

    rules = (
        Rule(LinkExtractor(allow=r'/?page=\d+$')),
        Rule(LinkExtractor(allow=r'/genres/\d+$')),
        Rule(LinkExtractor(allow=r'/books/\d+/$'), callback='parse_item', follow=True),
    )

    def parse_item(self, response:Response):
        #self.logger.info(response.url)
        loader = LabirintLoader(item=BooksItem(), response=response)
        loader.add_value('link', response.url)
        loader.add_css('name', 'meta[property="og:title"]::attr(content)')
        loader.add_css('authors', 'div.authors a::text')
        loader.add_css('price', 'span.buying-pricenew-val-number::text')
        loader.add_css('price', 'span.buying-price-val-number::text')
        loader.add_css('price_old', 'span.buying-priceold-val-number::text')
        loader.add_css('rating', '#rate::text')
        return loader.load_item()

class LabirintLoader(BooksLoader):
    #приводим к диапазону 0..10 -> 0..5
    #todo: сделать отдельную функцию с try/except
    rating_in = MapCompose(lambda v: float(v) / 2)
