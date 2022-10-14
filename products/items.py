# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from itemloaders.processors import MapCompose, TakeFirst, Compose, Identity
from scrapy.loader import ItemLoader
import re

def process_price(value):
    try:
        return int(re.sub(r'\D+', '', value))
    except:
        return value

def process_characteristics(value):
    result = {}
    backup = value.copy()
    try:
        while value: result |= {value.pop(0): value.pop(0)}
    except:
        result = backup

    return result

class ProductsItem(Item):
    url = Field()
    name = Field()
    price = Field()
    images = Field()
    characteristics = Field()

class ProductsLoader(ItemLoader):
    default_output_processor = TakeFirst()
    price_in = MapCompose(process_price)
    images_out = Identity()
    characteristics_in = Compose(process_characteristics)
    characteristics_out = Identity()
