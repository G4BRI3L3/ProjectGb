from flask import Flask, render_template, request, redirect, url_for, g, flash, session
import sqlite3
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_chiave_segreta_molto_sicura'
app.config['DATABASE'] = 'site.db'

def get_db():
    if '_database' not in g:
        g._database = sqlite3.connect(app.config['DATABASE'])
        g._database.row_factory = sqlite3.Row
    return g._database

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

app.cli.add_command(init_db_command)

# Funzione helper per il controllo dell'accesso
def login_required(view):
    def wrapped_view(**kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return view(**kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view

# Modifica la route index per redirigere al login
@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT id, name, ingredients, procedure, star_rating FROM recipe ORDER BY id DESC')
    recipes = cur.fetchall()
    return render_template('home.html', recipes=recipes)


# Aggiorna la route di login per impostare la sessione
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('index'))  # Reindirizza alla home page se il login è corretto
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        existing_user = db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone()
        if existing_user is None:
            db.execute('INSERT INTO user (username, email, password_hash) VALUES (?, ?, ?)',
                       (username, email, generate_password_hash(password)))
            db.commit()
            flash('La registrazione è avvenuta con successo!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Questo username è già in uso. Prova con un altro.', 'error')
    return render_template('register.html')

@app.route('/recipe/new', methods=['GET', 'POST'])
@login_required
def new_recipe():
    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        procedure = request.form['procedure']
        user_id = session['user_id']
        db = get_db()
        db.execute('INSERT INTO recipe (name, ingredients, procedure, user_id) VALUES (?, ?, ?, ?)',
                   (name, ingredients, procedure, user_id))
        db.commit()
        return redirect(url_for('index'))
    return render_template('recipe_form.html')

@app.route('/recipe/<int:recipe_id>')
@login_required
def view_recipe(recipe_id):
    db = get_db()
    recipe = db.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()
    return render_template('recipe_view.html', recipe=recipe)

if __name__ == '__main__':
    app.run(debug=True)
    