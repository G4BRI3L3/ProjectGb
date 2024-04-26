-- schema.sql
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS recipe;
ALTER TABLE recipe ADD COLUMN image_path TEXT;


CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    procedure TEXT NOT NULL,
    star_rating REAL DEFAULT 0,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user (id)
);