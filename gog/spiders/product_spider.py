import logging
import re
from w3lib.url import canonicalize_url, url_query_cleaner

from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
import scrapy
from urllib.parse import urlencode

from ..items import ProductItem, ProductItemLoader
import json
from scrapy.shell import inspect_response

def load_products(response):
    """Load a ProductItem from the product page response."""
    loader = ProductItemLoader(item=ProductItem(),response=response)
    url = url_query_cleaner(response.url, ['snr'], remove=True)
    url = canonicalize_url(url)
    loader.add_value('url', url)
    publisher = response.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " product-details-row ")][6]/div[2]/a[1]/span[2]/text()')
    if publisher is None:
        loader.add_xpath('developer','//div[contains(concat(" ", normalize-space(@class), " "), " product-details-row ")][5]/div[2]/a[1]/span[2]/text()')
        loader.add_xpath('publisher','//div[contains(concat(" ", normalize-space(@class), " "), " product-details-row ")][5]/div[2]/a[2]/span[2]/text()')
    else:
        loader.add_xpath('developer','//div[contains(concat(" ", normalize-space(@class), " "), " product-details-row ")][6]/div[2]/a[1]/span[2]/text()')
        loader.add_xpath('publisher','//div[contains(concat(" ", normalize-space(@class), " "), " product-details-row ")][6]/div[2]/a[2]/span[2]/text()')
    loader.add_xpath('release_date','//div[contains(concat(" ", normalize-space(@class), " "), " product-details-row ")][4]/div[2]/text()')
    loader.add_css('app_name', '.header__title ::text')
    loader.add_css('specs', '.game-features__title ::text')
    loader.add_css('genre', '.product-details__data span a.un ::text')

    try:
        price = response.css('.module-buy__info > meta:nth-child(2) ::attr(content)').extract_first()
        price_disc = price
    except:
        price = None
        price_disc = price

    if price is None:
        price = '0.00'
        price_disc = price
    loader.add_value('price', price)
    loader.add_value('discount_price', price_disc)
    

    loader.add_css('rating', 'div.average-rating:nth-child(1) > meta:nth-child(4) ::attr(content)')
    
    return loader.load_item()


class ProductSpider(scrapy.Spider):
    name = 'products'
    # start_urls = ['https://www.gog.com/games']

    allowed_domains = ['gog.com']
    custom_settings = {
'SELENIUM_DRIVER_NAME' : 'firefox',
'SELENIUM_DRIVER_EXECUTABLE_PATH' : 'geckodriver',
'SELENIUM_DRIVER_ARGUMENTS' : ['--headless'],
'BOT_NAME' : 'gog',
'SPIDER_MODULES' : ['gog.spiders'],
'NEWSPIDER_MODULE' : 'gog.spiders',
'USER_AGENT' : 'GOG Scraper',
'ROBOTSTXT_OBEY' : True,
'DOWNLOAD_DELAY' : 1,
'DOWNLOADER_MIDDLEWARES' :{
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'gog.middlewares.SeleniumMiddleware': 800
},
'AUTOTHROTTLE_ENABLED' : True,
'HTTPCACHE_ENABLED' : False,
'HTTPCACHE_EXPIRATION_SECS' : 0,  # Never expire.
'HTTPCACHE_DIR' : 'httpcache',
'HTTPCACHE_IGNORE_HTTP_CODES' : [301, 302, 303, 306, 307, 308],
'HTTPCACHE_STORAGE' : 'gog.middlewares.GOGCacheStorage',
'FEED_EXPORT_ENCODING' : 'utf-8',
'FEED_URI' : 'output/gog_products.jl',
'FEED_FORMAT' : 'jsonlines',
'LOG_LEVEL' : 'WARNING',
'LOG_FILE' : 'output/gog_products.log'
}


    def start_requests(self):
        yield Request('https://www.gog.com/games/ajax/filtered?mediaType=game&sort=popularity&page=1',self.parse)

    def parse_product(self, response):
        # print(response)
        # Circumvent age selection form.
        yield load_products(response)

    def process_the_links(self, links):
        
        for link in links:
            print(link.url)  # fix url to avoid unnecessary redirection
            yield link

    

    def parse(self,response):
        # print(response.body_as_unicode())
        # data = re.findall(r'(\"products\".+\});',response.body_as_unicode())
        # data = '{' + data[0]
        jsonresponse = json.loads(response.body_as_unicode())
        products = jsonresponse['products']
        for product in products:
            prod_url = 'https://www.gog.com' + product['url']
            yield Request(url=prod_url,callback =self.parse_product,priority=1)

        # items = load_products(response)
        # for item in items:
        #     yield item

        try:
            page_num = int(re.findall(r'\d+$',str(response.url))[0])
        except:
            page_num=0
        if page_num > 2000:
            raise scrapy.exceptions.CloseSpider('YU DONE')
        page_num = page_num + 1
        page_num = str(page_num)
        params = {
            'mediaType' : 'game',
            'sort' : 'popularity',
            'page' : page_num,

        }
        response_url = 'https://www.gog.com/games/ajax/filtered'
        new_url = response_url + '?' + urlencode(params)
        # print(new_url)
        yield Request(url=new_url,callback = self.parse,)
