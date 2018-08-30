import json
import db
import os
from datetime import datetime
from steam.spiders import product_spider
from gog.spiders import product_spider
import steam
import gog
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_crawls():
    process = CrawlerProcess()
    process.crawl(gog.spiders.product_spider.ProductSpider)
    process.crawl(steam.spiders.product_spider.ProductSpider)
    process.start()

def run_gog_spider():
    process = CrawlerProcess()
    process.crawl('products')
    process.start()

def price_checker(price):
    if r'^\d.*' in price:
        return True
    else:
        return False

def check_data(game):
    attr = ['url','app_name','developer','publisher','release_date','specs','genre','price','discount_price','rating']
    for at in attr:
        try:
            game[at]
        except:
            if at is 'genre' or at is 'specs':
                game[at] = []
            else:
                game[at] = ''
    return game
    


def read_to_db():
    file_locations = {'steam':'output/steam_products.jl','gog':'output/gog_products.jl'}
    for location in file_locations:
        print(location)
        with open(file_locations[location]) as f:
            for line in f:
                game = json.loads(line)
                if location is 'steam':
                    if 'https://store.steampowered.com/app/' not in game['url']:
                        continue
                    game = check_data(game)
                    db.insert_game(game,location)
                if location is 'gog':
                    game = check_data(game)
                    db.insert_game(game,location)
        os.remove(file_locations[location]) 

if not os.environ.get("games"):
    os.environ["games"] = 'db_games.db'

start_time = datetime.now()
print('Running Crawlers')
run_crawls()
print('Done.\n')
print('Crawls took', datetime.now()-start_time, ' to complete\n')
read_to_db()



