import sqlite3
import os

# Suppression de la base de données existante si elle existe
if os.path.exists('carbon_footprint.db'):
    os.remove('carbon_footprint.db')

def init_db():
    with sqlite3.connect('carbon_footprint.db') as conn:
        cursor = conn.cursor()
        
        # Création de la table users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
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

if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès!") 