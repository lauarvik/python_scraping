# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.spiders import Spider
from scrapy.exceptions import DropItem
import pymongo

class BooksPipeline:
    collection_name = 'scrapy_books'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'books')
        )

    def open_spider(self, spider:Spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
    
    def close_spider(self, spider:Spider):
        self.client.close()

    def process_item(self, item, spider:Spider):
        coll = self.db[self.collection_name]
        doc = ItemAdapter(item).asdict()
        #создаём новое поле
        doc['site'] = spider.name
        #добавляем новые, обновялем старые (upsert=True)
        if not coll.update_one({'link': doc['link']}, {'$set': doc}, upsert=True).upserted_id:
            raise DropItem('Duplicate item found')
        else:
            return item
