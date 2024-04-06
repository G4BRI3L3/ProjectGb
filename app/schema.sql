-- SQLite
CREATE TABLE Utenti (
    UserID SERIAL PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL
);

CREATE TABLE Ricette (
    RicettaID SERIAL PRIMARY KEY,
    Titolo VARCHAR(100) NOT NULL,
    Descrizione TEXT NOT NULL,
    Procedura TEXT NOT NULL,
    DataPubblicazione DATE NOT NULL,
    UserID INT NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Utenti(UserID)
);


CREATE TABLE Ingredienti (
    IngredienteID SERIAL PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE RicettaIngrediente (
    RicettaIngredienteID SERIAL PRIMARY KEY,
    RicettaID INT NOT NULL,
    IngredienteID INT NOT NULL,
    Quantità VARCHAR(100),
    FOREIGN KEY (RicettaID) REFERENCES Ricette(RicettaID),
    FOREIGN KEY (IngredienteID) REFERENCES Ingredienti(IngredienteID)
);


CREATE TABLE Voti (
    VotoID SERIAL PRIMARY KEY,
    Punteggio INT CHECK (Punteggio >= 1 AND Punteggio <= 5),
    RicettaID INT NOT NULL,
    UserID INT NOT NULL,
    FOREIGN KEY (RicettaID) REFERENCES Ricette(RicettaID),
    FOREIGN KEY (UserID) REFERENCES Utenti(UserID),
    UNIQUE (RicettaID, UserID)
);


CREATE TABLE Recensioni (
    RecensioneID SERIAL PRIMARY KEY,
    Testo TEXT NOT NULL,
    Voto INT CHECK (Voto >= 1 AND Voto <= 5),
    Data DATE NOT NULL,
    RicettaID INT NOT NULL,
    UserID INT NOT NULL,
    FOREIGN KEY (RicettaID) REFERENCES Ricette(RicettaID),
    FOREIGN KEY (UserID) REFERENCES Utenti(UserID)
);
