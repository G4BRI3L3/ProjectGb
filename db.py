import sqlite3

DATABASE = 'site.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with open('schema.sql', 'r') as f:
        get_db().executescript(f.read())
