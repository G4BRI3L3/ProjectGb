import sqlite3

conn = sqlite3.connect ('site.db')
c = conn.cursor()

c.execute(
    '''
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (recipe_id) REFERENCES recipe (id),
    UNIQUE (user_id, recipe_id)  -- Questo assicura che la stessa ricetta non venga aggiunta più volte dagli stessi utenti
);

    '''

)

conn.commit()
conn.close()