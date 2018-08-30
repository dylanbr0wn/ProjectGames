#
# db.py
#
import re
import os
import sqlite3
import time
import datetime
import db_init

def test_db_conn():
    """ Check if db connection can open, create and init db if doesn't already exist """
    dbname = os.environ.get("games")
    assert dbname is not None

    # If db file doesn't exist call the initialize module to create and init
    if not os.path.isfile(dbname):
        db_init.init(dbname)

def get_db():
    dbname = os.environ.get("games")
    assert dbname is not None
    
    return sqlite3.connect(dbname)

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


# def get_games():
#     conn = get_db()
#     curs = conn.cursor()
#     rows = curs.execute ("SELECT * FROM polls_game ORDER BY name").fetchall()
#     games = []
#     for row in rows:
#         game = game_row_to_dict(row)
#         games.append(game)
#     return games

def create_new_game(game,site):
    conn = get_db()
    curs = conn.cursor()
    str = "INSERT INTO " + site + " (url, name, developer, publisher, release_date, specs, genre, price, discount_price, rating, last_updated) VALUES (?,?,?,?,?,?,?,?,?,?,?);"
    curs.execute(str, 
                (game['url'], game['app_name'], game['developer'], game['publisher'], game['release_date'], ",".join(game['specs']), ",".join(game['genre']), game['price'], game['discount_price'], game['rating'], time.time()))
    conn.commit()
    add_to_lookup(game,site)
    res = curs.execute("SELECT * FROM "+ site + " WHERE OID = (SELECT max(oid) FROM " + site + ")").fetchall()
    try:
        return game_row_to_dict(res[0])
    except:
        return game_row_to_dict(res)

def update_game(game,site):
    conn = get_db()
    curs = conn.cursor()
    str = "UPDATE " + site +  " SET price=?, discount_price=?, last_updated=? WHERE name=? COLLATE NOCASE;"
    curs.execute(str, 
                (game['price'], game['discount_price'], time.time(), game['app_name']))
    conn.commit()
    add_to_lookup(game,site)
    res = curs.execute("SELECT * FROM " + site + " WHERE name=? COLLATE NOCASE;",(game['app_name'],)).fetchall()
    if len(res) != 0:
        try:
            return game_row_to_dict(res[0])
        except:
            return game_row_to_dict(res)
    else:
       return None

def insert_game(game,site):
    conn = get_db()
    curs = conn.cursor()
    res = curs.execute("SELECT * FROM " + site + " WHERE name=? COLLATE NOCASE;",(game['app_name'],)).fetchall()
    if len(res) != 0:
       return update_game(game,site)
    else:
       return create_new_game(game,site)

def add_to_lookup(game,site):
    conn = get_db()
    curs = conn.cursor()
    # print(game['app_name'])
    lookup = 'SELECT * FROM lookup WHERE name=?'
    res = curs.execute(lookup,(game['app_name'],)).fetchall()
    game_lookup_name = re.sub('\'','\'\'',game['app_name'])
    if len(res) == 1:
        str = "UPDATE lookup SET " + site + "_lookup=? WHERE name=? ;"
        
        site_lookup = "SELECT * FROM " + site + " WHERE name='" + game_lookup_name + "' COLLATE NOCASE"
        # print(site_lookup)
        curs.execute(str, (site_lookup,game['app_name']))
        conn.commit()
    elif len(res) == 0:
        site_lookup = "SELECT * FROM " + site + " WHERE name='" + game_lookup_name + "' COLLATE NOCASE"
        if 'gog' in site:

            str = "INSERT INTO lookup (name, gog_lookup, steam_lookup) VALUES(?, ?, '')"
        elif 'steam' in site:
            str = "INSERT INTO lookup (name, gog_lookup, steam_lookup) VALUES(?, '', ?)"
        curs.execute(str,(game['app_name'],site_lookup))
        conn.commit()
    else:
        print('multiple entries found')


def get_rng_seed():
    """ Generate rng seed """
    return 0xDEADBEEF
