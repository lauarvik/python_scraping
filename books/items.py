# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Field, Item
from itemloaders.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
import re

def clean_rating(value):
    try:
        return float(value)
    except:
        return value

def clean_price(value):
    try:
        return int(re.sub(r'\D+', '', value))
    except:
        return value

class BooksItem(Item):
    link = Field()
    name = Field()
    authors = Field()
    price = Field()
    price_old = Field()
    rating = Field()

class BooksLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()
    authors_out = Join(', ')
    rating_in = MapCompose(clean_rating)
    price_old_in = MapCompose(clean_price)
    price_in = MapCompose(clean_price)
    