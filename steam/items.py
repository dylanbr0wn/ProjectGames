from datetime import datetime, date
import logging
import re
import calendar

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Join, MapCompose, TakeFirst

logger = logging.getLogger(__name__)


class StripText:
    def __init__(self, chars=' \r\t\n'):
        self.chars = chars

    def __call__(self, value):
        try:
            return value.strip(self.chars)
        except:  # noqa E722
            return value

def process_price(x):
    x= re.sub(r'CDN\$ ','',x)
    if 'Free' in x:
        x = '0.00'
    return x


def simplify_recommended(x):
    return True if x == 'Recommended' else False


def standardize_date(x):
    """
    Convert x from recognized input formats to desired output format,
    or leave unchanged if input format is not recognized.
    """
    try:
        time = datetime.strptime(x, '%d %b, %Y')
        return time
    except:
        return x

    

    


def str_to_float(x):
    x = x.replace(',', '')
    try:
        return float(x)
    except:  # noqa E722
        return x


def str_to_int(x):
    try:
        return int(str_to_float(x))
    except:  # noqa E722
        return x


class ProductItem(scrapy.Item):
    url = scrapy.Field()
    id = scrapy.Field()
    app_name = scrapy.Field()
    reviews_url = scrapy.Field()
    title = scrapy.Field()
    genre = scrapy.Field(
        output_processor=MapCompose(StripText())
    )
    developer = scrapy.Field()
    publisher = scrapy.Field()
    release_date = scrapy.Field(
        output_processor=Compose(TakeFirst(), StripText(), standardize_date)
    )
    specs = scrapy.Field(
        output_processor=MapCompose(StripText())
    )
    tags = scrapy.Field(
        output_processor=MapCompose(StripText())
    )
    price = scrapy.Field(
        output_processor=Compose(TakeFirst(),
                                 StripText(chars=' $\n\t\r'),
                                 process_price,
                                 str_to_float)
    )
    discount_price = scrapy.Field(
        output_processor=Compose(TakeFirst(),
                                 StripText(chars=' $\n\t\r'),
                                 process_price,
                                 str_to_float)
    )
    sentiment = scrapy.Field()
    n_reviews = scrapy.Field(
        output_processor=Compose(
            MapCompose(StripText(), lambda x: x.replace(',', ''), str_to_int),
            max
        )
    )
    rating = scrapy.Field(
        output_processor=Compose(TakeFirst(), StripText(), str_to_int)
    )
    early_access = scrapy.Field()


class ReviewItem(scrapy.Item):
    product_id = scrapy.Field()
    page = scrapy.Field()
    page_order = scrapy.Field()
    recommended = scrapy.Field(
        output_processor=Compose(TakeFirst(), simplify_recommended),
    )
    date = scrapy.Field(
        output_processor=Compose(TakeFirst(), standardize_date)
    )
    text = scrapy.Field(
        input_processor=MapCompose(StripText()),
        output_processor=Compose(Join('\n'), StripText())
    )
    hours = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_float)
    )
    found_helpful = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    found_unhelpful = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    found_funny = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    compensation = scrapy.Field()
    username = scrapy.Field()
    user_id = scrapy.Field()
    products = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    early_access = scrapy.Field()


class ProductItemLoader(ItemLoader):
    default_output_processor = Compose(TakeFirst(), StripText())


class ReviewItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
