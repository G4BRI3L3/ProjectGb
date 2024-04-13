-- SQLite
CREATE TABLE Utente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE Ricetta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titolo TEXT NOT NULL,
    descrizione TEXT NOT NULL,
    procedimento TEXT NOT NULL,
    data_pubblicazione DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_utente INTEGER NOT NULL,
    FOREIGN KEY (id_utente) REFERENCES Utente (id)
);

CREATE TABLE Ingrediente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    quantita TEXT NOT NULL
);

CREATE TABLE Ricetta_Ingrediente (
    id_ricetta INTEGER,
    id_ingrediente INTEGER,
    PRIMARY KEY (id_ricetta, id_ingrediente),
    FOREIGN KEY (id_ricetta) REFERENCES Ricetta (id),
    FOREIGN KEY (id_ingrediente) REFERENCES Ingrediente (id)
);

CREATE TABLE Voto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    punteggio INTEGER CHECK(punteggio >= 1 AND punteggio <= 5),
    id_ricetta INTEGER,
    id_utente INTEGER,
    UNIQUE (id_ricetta, id_utente),
    FOREIGN KEY (id_ricetta) REFERENCES Ricetta (id),
    FOREIGN KEY (id_utente) REFERENCES Utente (id)
);

CREATE TABLE Recensione (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    testo TEXT NOT NULL,
    id_ricetta INTEGER,
    id_utente INTEGER,
    FOREIGN KEY (id_ricetta) REFERENCES Ricetta (id),
    FOREIGN KEY (id_utente) REFERENCES Utente (id)
);