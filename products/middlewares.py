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

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response:HtmlResponse, result, spider:Spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response:HtmlResponse, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

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
            if cookies and request.cookies.get('qrator_jsid') != cookies.get('qrator_jsid'):
                request.cookies['qrator_jsid'] = cookies.get('qrator_jsid')
        return None

    def process_response(self, request:Request, response:HtmlResponse, spider:Spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        if response.status == 401:
            from urllib.parse import urlparse
            p = urlparse(response.url)
            if not p.netloc in ['leroymerlin.ru']:
                return response

            import requests, re
            cookies = response.headers.getlist('Set-Cookie')
            for coo in cookies:
                if match := re.match('qrator_jsr=(.+?)-(.+?)-', coo.decode('utf-8')):
                    nonce, qsessid = match.groups()
                    spider.logger.info('Подбор знаничения pow')
                    session = requests.Session()
                    pow = 0
                    status = 403
                    while status == 403 and pow < 1280:
                        if not pow % 10:
                            print('.', end='', flush=True)

                        pow += 1
                        url = '%s://%s/__qrator/validate?pow=%s&nonce=%s&qsessid=%s' % (p.scheme, p.netloc, pow, nonce, qsessid)
                        r = session.post(url, json={})
                        if (status := r.status_code) == 200: break

                    else:
                        print()
                        spider.logger.error('Перебор pow завершился ничем. [%s]' % status)
                        return response
                    
                    print()
                    cookies = r.cookies.get_dict()
                    if qrator_jsid := cookies.get('qrator_jsid'):
                        spider.logger.info('Значение найдено: pow=%s, qrator_jsid=%s' % (pow, qrator_jsid))
                        if hasattr(spider, 'state'):
                            if not isinstance(spider.state.get('cookies'), dict):
                                spider.state['cookies'] = {}
                            
                            spider.state['cookies'].update(cookies)

                        return response.follow(response.url, cookies=request.cookies.update(cookies))
                    #break # for coo in cookies:

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
