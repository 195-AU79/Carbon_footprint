import sqlite3
import os

# Suppression de la base de données existante si elle existe
if os.path.exists('carbon_footprint.db'):
    os.remove('carbon_footprint.db')

# Connexion à la base de données
conn = sqlite3.connect('carbon_footprint.db')
cursor = conn.cursor()

# Création de la table users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

# Création de la table results
cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    electricity REAL,
    gasoline REAL,
    diesel REAL,
    natural_gas REAL,
    flight REAL,
    total_emissions REAL,
    reduction_rate REAL DEFAULT 0,
    activity_growth REAL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

conn.commit()
conn.close()
print("Base de données initialisée avec succès!") 