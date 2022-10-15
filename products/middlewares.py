# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, Spider
from scrapy.http import Request, HtmlResponse
from scrapy.exceptions import IgnoreRequest

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class ProductsSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response:HtmlResponse, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        spider.logger.info('MIDDLEWARE: process_spider_input, %s' % response.status)
        if response.status == 401:
            #spider.logger.info('MIDDLEWARE: %s' % response.request.cookies)
            #spider.logger.info('MIDDLEWARE: %s' % spider.state.get('cookies'))
            #response.request.cookies = spider.state.get('cookies')
            raise Exception('MIDDLEWARE: не пропущу')
            #pass
        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response:HtmlResponse, result, spider:Spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        spider.logger.info('MIDDLEWARE: process_spider_output, %s' % response.status)
        # Must return an iterable of Request, or item objects.
        for i in result:
            spider.logger.info('MIDDLEWARE: result = %s' % i)
            yield i

    def process_spider_exception(self, response:HtmlResponse, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.
        spider.logger.info('MIDDLEWARE: process_spider_exception')
        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.
        spider.logger.info('MIDDLEWARE: process_start_requests')
        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider:Spider):
        spider.logger.info('Павук открыт: %s' % spider.name)


class ProductsDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request:Request, spider:Spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        if hasattr(spider, 'state'):
            cookies = spider.state.get('cookies')
            if cookies and request.cookies != cookies:
                request.cookies = cookies
        return None

    def process_response(self, request:Request, response:HtmlResponse, spider:Spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        if response.status == 401:
            spider.logger.info('cookies: %s, state: %s' % (request.cookies, spider.state.get('cookies')))
            from urllib.parse import urlparse
            p = urlparse(response.url)
            if not p.netloc in ['leroymerlin.ru']:
                return response

            import requests, re
            if cookie := response.headers.get('Set-Cookie'):
                if match := re.search(r'qrator_jsr=(\d+\.\d+\..+?)-(.+?)-', cookie.decode('utf-8')):
                    nonce, qsessid = match.groups()
                    spider.logger.info('Подбор знаничения pow')
                    session = requests.Session()
                    pow = 0
                    status = 403
                    while status == 403 and pow < 1024:
                        if not pow % 10:
                            print('.', end='', flush=True)

                        pow += 1
                        url = f'{p.scheme}://{p.netloc}/__qrator/validate?pow={pow}&nonce={nonce}&qsessid={qsessid}'
                        r = session.post(url, json={})
                        if (status := r.status_code) == 200: break

                    else:
                        spider.logger.error(f'Перебор pow завершился ничем. status: {status}')
                        return response
                    
                    print()
                    cookie = r.headers.get('Set-Cookie')
                    if match := re.search(r'(qrator_jsid)=(.+)', str(cookie)):
                        _, qrator_jsid = match.groups()
                        spider.logger.info(f'Значение найдено: pow={pow}, qrator_jsid={qrator_jsid}')
                        cookies = dict(qrator_jsid=qrator_jsid)
                        if hasattr(spider, 'state'):
                            spider.state['cookies'] = cookies

                        return response.follow(response.url, cookies=cookies)

        return response

    def process_exception(self, request, exception, spider:Spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        #spider.logger.info('MIDDLEWARE: process_exception, %s' % request.cookies)
        pass

    def spider_opened(self, spider:Spider):
        spider.logger.info('Павук открыт: %s' % spider.name)
