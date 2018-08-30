"""
Initialize SQLite database.
Should only be called when one doesn't already exist
"""
import sys
import os
import sqlite3

def init(dbname):
    """ Initialize database with name dbname """
    assert dbname is not None

    # Connect & get db cursor
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()

    # Double check tables don't already exist, quit if so
    tab = curs.execute ("SELECT * FROM sqlite_master WHERE type='table' AND name='polls_game'").fetchall()
    if len(tab) > 0:
        print("table games exists in current directory.")
        print("Please delete ", dbname, " before running this script.")
        sys.exit(0)


    # Create tables
    print("Initialize with Django")

def drop_database(dbname):
    assert 'test' in dbname  # dont delete prod data! 
    try:
        os.remove(dbname)
    except OSError:
        pass
