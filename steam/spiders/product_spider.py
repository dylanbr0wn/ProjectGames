import logging
import re
from w3lib.url import canonicalize_url, url_query_cleaner
import scrapy

from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlencode

from ..items import ProductItem, ProductItemLoader

logger = logging.getLogger(__name__)


def load_product(response):
    """Load a ProductItem from the product page response."""
    loader = ProductItemLoader(item=ProductItem(), response=response)

    url = url_query_cleaner(response.url, ['snr'], remove=True)
    url = canonicalize_url(url)
    loader.add_value('url', url)

    found_id = re.findall('/app/(.*?)/', response.url)
    if found_id:
        id = found_id[0]
        reviews_url = f'http://steamcommunity.com/app/{id}/reviews/?browsefilter=mostrecent&p=1'
        loader.add_value('reviews_url', reviews_url)
        loader.add_value('id', id)

    # Publication details.
    genre = response.css('.block_content_inner .details_block').extract_first()
    genre = genre.split('<br>')
    genre = re.findall(r'>([a-zA-Z]*?)<',genre[1])
    loader.add_value('genre',genre)

    devpub = response.css('.details_block .dev_row a ::text').extract()
    try:
        developer = devpub[0]
        publisher = devpub[1]
    except:
        try:
            developer = devpub[0]
            publisher = ''
        except:
            developer = ''
            publisher = ''

    loader.add_value('developer',developer)
    loader.add_value('publisher',publisher)
    release = response.css('.block_content_inner .details_block').extract_first()
    try:
        release = release.split('<br>')
    except:
        pass
    release = re.findall(r'<b>Release Date:</b>(.*)',release[2])
    early_access = response.css('.early_access_header')
    coming_soon = response.css('.game_area_comingsoon')
    if early_access or coming_soon:
        loader.add_value('early_access', True)
        loader.add_value('release_date', 'Not Yet Released')

    else:
        loader.add_value('release_date', release)
        loader.add_value('early_access', False)
    


    loader.add_css('app_name', '.apphub_AppName ::text')
    loader.add_css('specs', '.game_area_details_specs a ::text')
    loader.add_css('tags', 'a.app_tag::text')

    price = response.css('.game_purchase_price ::text').extract_first()
    if not price:
        price = response.css('.discount_original_price ::text').extract_first()
        loader.add_css('discount_price', '.discount_final_price ::text')
    loader.add_value('price', price)

    sentiment = response.css('.game_review_summary').xpath(
        '../*[@itemprop="description"]/text()').extract()
    loader.add_value('sentiment', sentiment)
    loader.add_css('n_reviews', '.responsive_hidden', re='\(([\d,]+) reviews\)')

    loader.add_xpath(
        'rating',
        '//div[@id="game_area_metascore"]/div[contains(@class, "score")]/text()')

    early_access = response.css('.early_access_header')
    coming_soon = response.css('.game_area_comingsoon')
    if early_access or coming_soon:
        loader.add_value('early_access', True)

    else:
        loader.add_value('early_access', False)

    return loader.load_item()


class ProductSpider(scrapy.Spider):
    name = 'products'
    start_urls = ['http://store.steampowered.com/search/?sort_by=Released_DESC']
    custom_settings = {
'BOT_NAME' : 'steam',
'SPIDER_MODULES' : ['steam.spiders'],
'NEWSPIDER_MODULE' : 'steam.spiders',
'USER_AGENT' : 'Steam Scraper',
'ROBOTSTXT_OBEY' : True,
'DOWNLOADER_MIDDLEWARES' :{
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'steam.middlewares.CircumventAgeCheckMiddleware': 600,
},
'AUTOTHROTTLE_ENABLED' : True,
'DUPEFILTER_CLASS' : 'steam.middlewares.SteamDupeFilter',
'HTTPCACHE_ENABLED' : False,
'HTTPCACHE_EXPIRATION_SECS' : 0,  # Never expire.
'HTTPCACHE_DIR' : 'httpcache',
'HTTPCACHE_IGNORE_HTTP_CODES' : [301, 302, 303, 306, 307, 308],
'HTTPCACHE_STORAGE' : 'steam.middlewares.SteamCacheStorage',
'FEED_EXPORT_ENCODING' : 'utf-8',
'FEED_URI' : 'output/steam_products.jl',
'FEED_FORMAT' : 'jsonlines',
'LOG_LEVEL' : 'INFO',
'LOG_FILE' : 'output/steam_products.log'
}

    allowed_domains = ['steampowered.com']

   


    def start_requests(self):
        
        yield scrapy.Request('http://store.steampowered.com/search/?sort_by=Released_DESC',self.parse)

    def parse(self,response):
        # print(response.url)
        links = LinkExtractor(allow='/app/(.+)/', restrict_css='#search_result_container').extract_links(response)
        for link in links:
            # print(link.url)
            for allowed_domain in self.allowed_domains:
                if allowed_domain in link.url:
                    is_allowed = True
            if is_allowed:
                yield scrapy.Request(url = link.url,callback = self.parse_product)
        
        try:
            page_num = int(re.findall(r'page=(\d+)',str(response.url))[0])
        except:
            page_num=0
        if page_num > 3000:
            raise scrapy.exceptions.CloseSpider('YU DONE')
        
        page_num = page_num +1

        querystring = {"sort_by":"Released_DESC","page": page_num,"hide_filtered_results_warning":"1"}
        response_url = 'https://store.steampowered.com/search/results'
        new_url = response_url + '?' + urlencode(querystring)
        yield scrapy.Request(url=new_url,callback = self.parse,)



    def parse_product(self, response):
        # Circumvent age selection form.
        if '/agecheck/app' in response.url:
            logger.debug(f'Form-type age check triggered for {response.url}.')

            form = response.css('#agegate_box form')

            action = form.xpath('@action').extract_first()
            name = form.xpath('input/@name').extract_first()
            value = form.xpath('input/@value').extract_first()

            formdata = {
                name: value,
                'ageDay': '1',
                'ageMonth': '1',
                'ageYear': '1955'
            }

            yield FormRequest(
                url=action,
                method='POST',
                formdata=formdata,
                callback=self.parse_product
            )

        else:
            yield load_product(response)
