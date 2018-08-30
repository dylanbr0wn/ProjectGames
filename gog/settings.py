#from smart_getenv import getenv
from shutil import which

BOT_NAME = 'gog'

SPIDER_MODULES = ['gog.spiders']
NEWSPIDER_MODULE = 'gog.spiders'

USER_AGENT = 'GOG Scraper'

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY=5.0



SELENIUM_DRIVER_NAME='firefox'
SELENIUM_DRIVER_EXECUTABLE_PATH=which('geckodriver')
SELENIUM_DRIVER_ARGUMENTS=['-headless']

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'gog.middlewares.SeleniumMiddleware': 800
}


# DOWNLOAD_HANDLERS = {
#     'http' : 'gog.handlers.PhantomJSDownloadHandler',
#     'https' : 'gog.handlers.PhantomJSDownloadHandler',
# }

AUTOTHROTTLE_ENABLED = True



HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0  # Never expire.
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [301, 302, 303, 306, 307, 308]
HTTPCACHE_STORAGE = 'gog.middlewares.GOGCacheStorage'

#AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID', type=str, default=None)
#AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY', type=str, default=None)

FEED_EXPORT_ENCODING = 'utf-8'
FEED_URI = 'output/gog_products.jl'
FEED_FORMAT = 'jsonlines'

LOG_LEVEL = 'WARNING'
LOG_FILE = 'output/gog_products.log'