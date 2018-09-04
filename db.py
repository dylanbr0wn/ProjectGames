#
# db.py
#
import re
import os
import psycopg2
import time
import datetime
import db_init
from psycopg2 import sql


def get_db():
    conn = psycopg2.connect(user='postgres', password='connect',
                        host='localhost', port='5432',dbname='games')
    return conn

def close_db(conn):
	conn.close()

#CREATE TABLE games (game_name STRING, price INTEGER, date_updated DATE, haveResult BOOLEAN);
def game_row_to_dict(row):
    game = {}
    game['id'] = row[0]
    game['url'] = row[1]
    game['name'] = row[2]
    game['developer'] = row[3]
    game['publisher'] = row[4]
    game['release_date'] = row[5]
    game['specs'] = row[6]
    game['genre'] = row[7]
    game['price'] = row[8]
    game['discount_price'] = row[9]
    game['rating'] = row[10]
    game['last_updated'] = datetime.datetime.utcfromtimestamp(row[11])
    return game


def create_new_game(game,site):
    conn = get_db()
    curs = conn.cursor()
    query = sql.SQL("INSERT INTO {} ({}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);").format(sql.Identifier(site), sql.SQL(', ').join([sql.Identifier('url'), sql.Identifier('name'), sql.Identifier('developer'), sql.Identifier('publisher'), sql.Identifier('release_date'), sql.Identifier('specs'), sql.Identifier('genre'), sql.Identifier('price'), sql.Identifier('discount_price'), sql.Identifier('rating'), sql.Identifier('last_updated')]),)
    # print(query.as_string(conn))
    curs.execute(query.as_string(conn), [game['url'], game['app_name'], game['developer'], game['publisher'], game['release_date'], ",".join(game['specs']), ",".join(game['genre']), game['price'], game['discount_price'], game['rating'], time.time()])
    conn.commit()
    add_to_lookup(game,site)

def update_game(game,site):
    conn = get_db()
    curs = conn.cursor()
    
    str = sql.SQL("UPDATE {} SET {} = %s, {} = %s, {} = %s WHERE {} = %s;").format(sql.Identifier(site),sql.Identifier('price'), sql.Identifier('discount_price'), sql.Identifier('last_updated'), sql.Identifier('name'))
    curs.execute(str.as_string(conn), 
                (game['price'], game['discount_price'], time.time(),game['app_name'],))
    conn.commit()
    add_to_lookup(game,site)

def insert_game(game,site):
    conn = get_db()
    curs = conn.cursor()
    curs.execute("set enable_indexscan = off;")
    curs.execute("set enable_indexonlyscan = off;")
    curs.execute("set enable_bitmapscan = off;")
    # query = 'select * from "{}" where "{}" = %s;'.format(site,'name')
    query = sql.SQL("select * from {} where {} = %s;").format(sql.Identifier(site),sql.Identifier('name')).as_string(conn)
    # print(query)
    curs.execute(query,(game['app_name'],))
    res = curs.fetchall()
    # print(res)
    if len(res) == 0:
        create_new_game(game,site)
    elif len(res) != 0:
       update_game(game,site)

def add_to_lookup(game,site):
    conn = get_db()
    curs = conn.cursor()
    # print(game['app_name'])
    lookup = sql.SQL('SELECT * FROM {} WHERE {} = %s;').format(sql.Identifier('lookup'),sql.Identifier('name')).as_string(conn)
    print(lookup)
    curs.execute(lookup, (game['app_name'],))
    res =  curs.fetchall()
    print(res)
    site_lookup = sql.SQL("SELECT * FROM {} WHERE {} = {}").format(sql.Identifier(site),sql.Identifier('name'), sql.Literal(game['app_name'])).as_string(conn)
    if len(res) == 0:
        
        if 'gog' in site:

            str = sql.SQL("INSERT INTO {} ({}) VALUES(%s, %s,'');").format(sql.Identifier('lookup'),sql.SQL(', ').join([sql.Identifier('name'),sql.Identifier('gog_lookup'),sql.Identifier('steam_lookup')]))
            print(str)
            curs.execute(str.as_string(conn),[game['app_name'],site_lookup])
        elif 'steam' in site:
            str = sql.SQL("INSERT INTO {} ({}) VALUES(%s, '', %s);").format(sql.Identifier('lookup'),sql.SQL(', ').join([sql.Identifier('name'),sql.Identifier('gog_lookup'),sql.Identifier('steam_lookup')]))
            curs.execute(str.as_string(conn),[game['app_name'],site_lookup])
        conn.commit()
    elif len(res) == 1:
       
        print(game['app_name'])
        str = sql.SQL("UPDATE {} SET {} = %s WHERE {} = %s ;").format(sql.Identifier('lookup'), sql.Identifier(site + '_lookup'),sql.Identifier('name'))
        
        
        # print(site_lookup)
        curs.execute(str.as_string(conn),(site_lookup,game['app_name'],))
        conn.commit()
        
    else:
        print('multiple entries found')


def get_rng_seed():
    """ Generate rng seed """
    return 0xDEADBEEF
