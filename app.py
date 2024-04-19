from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_chiave_segreta_molto_sicura'
app.config['DATABASE'] = 'ricette.db'

def get_db():
    if '_database' not in g:
        # Connessione al database SQLite
        g._database = sqlite3.connect(app.config['DATABASE'])
        g._database.row_factory = sqlite3.Row
    return g._database
# sium
print("ciao")
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
    """Clears the existing data and creates new tables."""
    init_db()
    click.echo('Initialized the database.')

app.cli.add_command(init_db_command)

# Route dell'app
@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT id, name, ingredients, procedure, star_rating FROM recipe ORDER BY id DESC')
    recipes = cur.fetchall()
    return render_template('home.html', recipes=recipes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            # Qui dovresti gestire la sessione dell'utente
            flash('Login successful!')
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        if db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
            flash(f"User {username} is already registered.")
        else:
            db.execute(
                'INSERT INTO user (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/recipe/new', methods=['GET', 'POST'])
def new_recipe():
    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        procedure = request.form['procedure']
        # Qui dovresti recuperare l'id dell'utente dalla sessione
        user_id = 1  # Assumi che l'utente sia già autenticato con id = 1
        db = get_db()
        db.execute(
            'INSERT INTO recipe (name, ingredients, procedure, user_id) VALUES (?, ?, ?, ?)',
            (name, ingredients, procedure, user_id)
        )
        db.commit()
        return redirect(url_for('index'))
    return render_template('recipe_form.html')

@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    db = get_db()
    recipe = db.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()
    return render_template('recipe_view.html', recipe=recipe)

if __name__ == '__main__':
    app.run(debug=True)