from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http.response import Response
from books.items import BooksItem, BooksLoader
from itemloaders.processors import MapCompose
import re

class Book24Spider(CrawlSpider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['http://book24.ru/']

    rules = (
        Rule(LinkExtractor(allow=r'/page-\d+/$')),
        Rule(LinkExtractor(allow=r'/catalog/.+-\d+/$')),
        Rule(LinkExtractor(allow=r'/product/.+-\d+/$'), callback='parse_item', follow=True),
    )

    def parse_item(self, response:Response):
        #self.logger.info(response.url)
        loader = Book24Loader(item=BooksItem(), response=response)
        loader.add_value('link', response.url)
        loader.add_css('name', '.breadcrumbs__item._last-item ::text')
        #loader.add_css('authors', '.product-characteristic__value ::text')
        loader.add_xpath('authors', '(//div[@class="product-characteristic__value"]//text())[1]')
        loader.add_css('price', 'meta[itemprop=price]::attr(content)')
        loader.add_css('price_old', '.product-sidebar-price__price-old::text')
        loader.add_css('rating', '.rating-widget__main-text::text')
        return loader.load_item()

class Book24Loader(BooksLoader):
    rating_in = MapCompose(lambda v: v.replace(',', '.'), BooksLoader.rating_in)
