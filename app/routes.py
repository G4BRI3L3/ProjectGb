from app import app
from flask import render_template, request, redirect, url_for
from .db import get_db

@app.route('/')
def index():
    db = get_db()
    ricette = db.execute('SELECT * FROM ricette').fetchall()
    return render_template('index.html', ricette=ricette)