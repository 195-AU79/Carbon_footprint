import sqlite3
from werkzeug.security import generate_password_hash

# Connexion à la base de données
conn = sqlite3.connect('carbon_footprint.db')
cursor = conn.cursor()

# Informations de l'utilisateur
username = input("Entrez votre nom d'utilisateur : ")
password = input("Entrez votre mot de passe : ")
email = input("Entrez votre email : ")

# Hashage du mot de passe avec la méthode pbkdf2:sha256
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

try:
    # Insertion du nouvel utilisateur
    cursor.execute('''
    INSERT INTO users (username, email, password)
    VALUES (?, ?, ?)
    ''', (username, email, hashed_password))
    
    # Validation des changements
    conn.commit()
    print("Compte créé avec succès!")

except sqlite3.IntegrityError:
    print("Erreur: Ce nom d'utilisateur ou email existe déjà.")

except Exception as e:
    print(f"Erreur lors de la création de l'utilisateur: {e}")

finally:
    # Fermeture de la connexion
    conn.close()