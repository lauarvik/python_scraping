from scrapy.http import Request, HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from products.items import ProductsItem, ProductsLoader

class LeroymerlinSpider(CrawlSpider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    custom_settings = {
        'DOWNLOAD_DELAY': 1.25,
        'CONCURRENT_REQUESTS':  4,
        'JOBDIR': 'crawls/' + name,
    }

    rules = (
        Rule(LinkExtractor(allow=r'page=\d+$')),
        Rule(LinkExtractor(allow=r'/product/.+-\d+/$'), callback='parse_item', follow=True),
    )

    def __init__(self, *a, **kw):
        q = kw.get('q', 'удиви меня')
        self.start_urls = ['https://leroymerlin.ru/search/?q=%s&page=1' % q]
        super().__init__(*a, **kw)

    def parse_item(self, response:HtmlResponse):
        loader = ProductsLoader(item=ProductsItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_css('name', 'h1 ::text')
        loader.add_css('price', 'span[slot="price"]::text')
        loader.add_css('images', 'picture[slot] img::attr(src)')
        loader.add_css('characteristics','#characteristics dl ::text')
        return loader.load_item()
