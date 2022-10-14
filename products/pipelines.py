# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re, os.path
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.spiders import Spider
from scrapy.exceptions import DropItem
import pymongo


class ProductsPipeline:
    collection_name = 'scrapy_products'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'products')
        )

    def open_spider(self, spider:Spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
    
    def close_spider(self, spider:Spider):
        self.client.close()

    def process_item(self, item, spider:Spider):
        coll = self.db[self.collection_name]
        doc = ItemAdapter(item).asdict()
        #добавляем новые, обновялем старые (upsert=True)
        if not coll.update_one({'url': doc['url']}, {'$set': doc}, upsert=True).upserted_id:
            #raise DropItem('Duplicate item found')
            pass
        
        return item

class ProductsImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item.get('images'):
            for img in item['images']:
                try:
                    yield Request(img)
                except Exception as e:
                    print(e)
            
    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        try:
            parts = item['url'].split('/')
            dir = parts[-1] if parts[-1] else parts[-2]
        except Exception as e:
            dir = ''
        
        return os.path.join(dir, os.path.basename(request.url))
