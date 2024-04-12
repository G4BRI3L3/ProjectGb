from app import app
from flask import render_template, request
import sqlite3

DATABASE = 'site.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    conn = get_db_connection()
    ricette = conn.execute('SELECT * FROM Ricetta').fetchall()
    conn.close()
    return render_template('home.html', ricette=ricette)

# Qui aggiungerai ulteriori funzionalità come la gestione delle ricette, degli ingredienti, dei voti e delle recensioni
