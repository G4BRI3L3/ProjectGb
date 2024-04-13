from flask import Flask
from db import init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Chiamata per inizializzare il database
init_db()

# Importa le viste dopo l'inizializzazione del db per evitare problemi di dipendenze circolari
from views import *

if __name__ == '__main__':
    app.run(debug=True)
