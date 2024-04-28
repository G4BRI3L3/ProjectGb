from flask import Flask, render_template, request, redirect, url_for, g, flash, session
import sqlite3
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_chiave_segreta_molto_sicura'
app.config['DATABASE'] = 'site.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


def get_db():
    db_path = app.config['DATABASE']
    if '_database' not in g:
        g._database = sqlite3.connect(db_path)
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
    # Recupera tutte le ricette e ordina per l'ID in ordine discendente
    cur = db.execute('SELECT id, name, ingredients, procedure, star_rating FROM recipe ORDER BY id DESC')
    recipes = cur.fetchall()
    # Converti ogni riga di recipes in un dizionario
    recipes_list = [dict(recipe) for recipe in recipes]
    
    # Calcola la media dei voti per ogni ricetta
    for recipe in recipes_list:
        rating_result = db.execute('SELECT AVG(rating) as average_rating FROM rating WHERE recipe_id = ?', (recipe['id'],)).fetchone()
        recipe['average_rating'] = rating_result['average_rating'] if rating_result['average_rating'] is not None else 'Not rated'
    
    return render_template('home.html', recipes=recipes_list)


# Aggiorna la route di login per impostare la sessione
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username+" "+password)
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', (username,)).fetchone()
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
    print("sium")
    if request.method == 'POST':
        print("entre!!")
        name = request.form['name']
        ingredients = request.form['ingredients']
        procedure = request.form['procedure']
        user_id = session['user_id']
        db = get_db()

        file = request.files.get('recipe_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            db.execute('INSERT INTO recipe (name, ingredients, procedure, user_id, image_path) VALUES (?, ?, ?, ?, ?)',
                       (name, ingredients, procedure, user_id, file_path))
            db.commit()
            return redirect(url_for('index'))
        else:
            flash('Allowed file types are - png, jpg, jpeg, gif', 'error')
    
    return render_template('recipe_form.html')



@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    db = get_db()
    # Recupera i dettagli della ricetta dal database
    recipe_data = db.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()
    recipe = dict(recipe_data)  # Converti in un dizionario mutabile

    # Recupera i commenti associati alla ricetta
    comments = db.execute(
        'SELECT comment.*, user.username FROM comment '
        'JOIN user ON comment.user_id = user.id '
        'WHERE recipe_id = ? ORDER BY comment.created_at DESC',
        (recipe_id,)
    ).fetchall()

    # Calcola la media dei voti per la ricetta
    rating_result = db.execute(
        'SELECT AVG(rating) as average_rating FROM rating '
        'WHERE recipe_id = ?',
        (recipe_id,)
    ).fetchone()
    # Aggiungi la media dei voti al dizionario della ricetta
    recipe['average_rating'] = rating_result['average_rating'] if rating_result['average_rating'] else 'Not yet rated'

    # Ottieni il voto corrente dell'utente, se esiste
    user_rating = None
    if 'user_id' in session:
        user_rating = db.execute(
            'SELECT rating FROM rating WHERE user_id = ? AND recipe_id = ?',
            (session['user_id'], recipe_id)
        ).fetchone()
        user_rating = user_rating['rating'] if user_rating else None

    return render_template('recipe_view.html', recipe=recipe, comments=comments, user_rating=user_rating)


@app.route('/recipe/<int:recipe_id>/comment', methods=['POST'])
@login_required
def submit_comment(recipe_id):
    text = request.form['comment_text']
    user_id = session['user_id']
    db = get_db()
    db.execute('INSERT INTO comment (user_id, recipe_id, text) VALUES (?, ?, ?)',
               (user_id, recipe_id, text))
    db.commit()
    return redirect(url_for('view_recipe', recipe_id=recipe_id))


@app.route('/recipe/<int:recipe_id>/rate', methods=['POST'])
@login_required
def rate_recipe(recipe_id):
    user_id = session['user_id']
    new_rating = request.form.get('rating')

    db = get_db()
    # Controlla se l'utente ha già votato
    existing_rating = db.execute(
        'SELECT rating FROM rating WHERE user_id = ? AND recipe_id = ?',
        (user_id, recipe_id)
    ).fetchone()

    if existing_rating:
        # Aggiorna il voto esistente
        db.execute(
            'UPDATE rating SET rating = ? WHERE user_id = ? AND recipe_id = ?',
            (new_rating, user_id, recipe_id)
        )
    else:
        # Inserisci un nuovo voto
        db.execute(
            'INSERT INTO rating (user_id, recipe_id, rating) VALUES (?, ?, ?)',
            (user_id, recipe_id, new_rating)
        )
    
    db.commit()
    flash('Grazie per il tuo voto!', 'success')
    return redirect(url_for('view_recipe', recipe_id=recipe_id))

@app.route('/add_to_favorites/<int:recipe_id>', methods=['POST'])
@login_required
def add_to_favorites(recipe_id):
    user_id = session['user_id']
    db = get_db()
    try:
        db.execute('INSERT INTO favorites (user_id, recipe_id) VALUES (?, ?)', (user_id, recipe_id))
        db.commit()
        flash('Recipe added to your favorites!', 'success')
    except sqlite3.IntegrityError:  # Gestisce il caso in cui la coppia user_id, recipe_id sia già presente
        flash('This recipe is already in your favorites!', 'info')
    return redirect(url_for('view_recipe', recipe_id=recipe_id))

@app.route('/my_favorites')
@login_required
def my_favorites():
    user_id = session['user_id']
    db = get_db()
    favorites = db.execute(
        'SELECT r.* FROM recipe r JOIN favorites f ON f.recipe_id = r.id WHERE f.user_id = ?',
        (user_id,)
    ).fetchall()
    return render_template('my_favorites.html', favorites=favorites)

@app.route('/remove_from_favorites/<int:recipe_id>', methods=['POST'])
@login_required
def remove_from_favorites(recipe_id):
    user_id = session['user_id']
    db = get_db()
    db.execute('DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?', (user_id, recipe_id))
    db.commit()
    flash('{{ Recipe removed from your favorites!', 'info')
    return redirect(url_for('my_favorites'))

if __name__ == '__main__':
    app.run(debug=True)
    