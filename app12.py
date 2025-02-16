# Importations de la bibliothèque standard
import io
import logging
import os
from pickle import FALSE
import sqlite3
import tempfile
from tkinter import TRUE


# Importations de bibliothèques tierces
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from psutil import users
from sqlalchemy import true
import xlsxwriter
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from flask import Flask, jsonify, render_template, request, send_file, redirect, url_for, flash
from fpdf import FPDF
from flask_cors import CORS
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration du logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import logger_config  # Importer le fichier log.py

print(logging.getLogger)  # Accéder à la variable
print(logger_config.setup_logger())  # Appeler la fonction


# Initialisation de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carbon_footprint.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def get_id(self):
        return str(self.id)

def init_db():
    try:
        conn = sqlite3.connect('carbon_footprint.db')
        cursor = conn.cursor()
        
        # Création de la table users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
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
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
    finally:
        if conn:
            conn.close()

# Vérification de l'existence de la base de données avant de se connecter
if not os.path.exists('carbon_footprint.db'):
    logger.error("La base de données carbon_footprint.db n'existe pas.")
    init_db()  # Appeler init_db pour créer les tables
else:
    logger.info("La base de données existe.")
    
    # Vérifiez si la table users existe
    conn = sqlite3.connect('carbon_footprint.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if not cursor.fetchone():
        logger.error("La table 'users' n'existe pas. Initialisation de la base de données.")
        init_db()  # Appeler init_db pour créer les tables
    conn.close()
            
# Fonction pour insérer un utilisateur dans la base de données
def ajouter_utilisateur(user, email, password):
    logger.debug(f"Tentative d'ajout de l'utilisateur: {user}")
    try:
        conn = sqlite3.connect('carbon_footprint.db')
        cursor = conn.cursor()
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        username = input 
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                       (username, email, hashed_password))
        conn.commit()
        flash("Compte créé avec succès!", "success")
    except sqlite3.IntegrityError:
        logger.error(f"Le nom d'utilisateur {username} existe déjà.")
        flash("Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre.", "danger")
    finally:
        if conn:
            conn.close()
            
# Vérification des identifiants
def verifier_utilisateur(username, password):
    try:
        user = Users.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            logger.info(f"L'utilisateur {username} a été vérifié avec succès.")
            return True
        else:
            logger.warning(f"Échec de la vérification pour l'utilisateur {username}.")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'utilisateur: {e}")
        return False

# Facteurs d'émission (kg CO2e par unité)
FACTORS = {
    "electricity": 0.05,   # kg CO2e par kWh
    "gasoline": 2.31,      # kg CO2e par litre
    "diesel": 2.68,        # kg CO2e par litre
    "natural_gas": 2.75,   # kg CO2e par m³
    "flight": 0.115        # kg CO2e par km
}



# Configuration du backend de Matplotlib avant d'importer pyplot
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend 'Agg' pour éviter les problèmes de GUI
import matplotlib.pyplot as plt

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_register'

@login_manager.user_loader

def load_user(user_id):
    try:
        return Users.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Erreur lors du chargement de l'utilisateur: {e}")
        return None

def load_user(user_name):
#    return Users.query.get(int(user_name))
    try:
        conn = sqlite3.connect('carbon_footprint.db')
        cursor = conn.cursor()
        cursor.execute( "SELECT id from users where users.username ?", (user_name,))
        user=cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la répuration de l'utilisateur: {e}")
        return False
    finally:
        if conn:
            conn.close()

    return( user )
# Initialisation de Dash APRÈS Flask
dash_app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


# Protection des routes Dash avec un middleware personnalisé
def protect_dash_views(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login_register'))
        return f(*args, **kwargs)
    return wrapper

# Routes Dash protégées
@app.route('/dash/')
@login_required
def render_dashboard():
    return dash_app.index()

@app.route('/dash/emissions')
@login_required
def emissions_dashboard():
    return dash_app.index()

@app.route('/dash/graphs')
@login_required
def graphs_dashboard():
    return dash_app.index()

def get_db_connection():
    conn = sqlite3.connect()
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@login_required
def index():
    logger.info(f"L'utilisateur {current_user.username} accède à la page d'index.")
    try:
        with sqlite3.connect() as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM results WHERE user_id = ?', (current_user.id,))
            results = cur.fetchall()  # Récupère les résultats pour l'utilisateur connecté
            return render_template('index.html', results=results)  # Passe les résultats au template
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données: {e}")
        return render_template('index.html', error='Une erreur est survenue lors de la récupération des données.')

@app.route('/login', methods=['GET', 'POST'])
def login_register():
    logger.debug("Accès à la page de connexion.")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.debug(f"Tentative de connexion avec le nom d'utilisateur: {username}")
        
        user = Users.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)  # Login l'utilisateur avec l'objet user, pas Users
            logger.info(f"Utilisateur {username} connecté avec succès.")
            return redirect(url_for('index'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")
            logger.warning(f"Échec de connexion pour l'utilisateur: {username}")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    logger.debug("Accès à la page d'inscription.")

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Vérifier que tous les champs sont remplis
        if not username or not password or not email:
            flash("Tous les champs sont requis.", "danger")
            logger.warning("Tentative d'inscription avec des champs vides.")
            return redirect(url_for('register'))

        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = Users.query.filter_by(username=username).first()
            if existing_user:
                flash("Ce nom d'utilisateur est déjà pris.", "danger")
                logger.warning(f"Tentative d'inscription avec un nom d'utilisateur déjà pris : {username}.")
                return redirect(url_for('register'))

            # Hashage du mot de passe
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Ajouter l'utilisateur à la base de données
            new_user = Users(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            # 🚀 Afficher un message seulement si l'inscription est bien prise en compte
            flash("✅ Inscription réussie ! Bienvenue, " + username + " 🎉", "success")
            logger.info(f"Nouvel utilisateur inscrit avec succès : {username}.")
            return redirect(url_for('login_register'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erreur lors de l'inscription : {e}")
            flash("Une erreur est survenue lors de l'inscription. Veuillez réessayer.", "danger")

    return render_template('register.html') # Affiche le formulaire d'inscription

@app.route('/logout')
@login_required
def logout():
    logger.info(f"L'utilisateur {current_user} se déconnecte.")
    logout_user()
    return redirect(url_for('login_register'))

@app.route('/calculate', methods=['POST'])
@login_required  # Assurez-vous que l'utilisateur est connecté
def calculate():
    """Route pour calculer les émissions de CO2e à partir du formulaire."""
    try:
        data = request.get_json()
        logger.debug(f"Données reçues : {data}")
        if not data:
            logger.error("Aucune donnée reçue.")
            return jsonify({'error': 'Aucune donnée reçue.'}), 400

        # Validation des données d'entrée
        required_fields = ['electricity', 'gasoline', 'diesel', 'natural_gas', 'flight']
        for field in required_fields:
            if field not in data:
                logger.error(f"Le champ {field} est manquant.")
                return jsonify({'error': f'Le champ {field} est manquant.'}), 400
            try:
                data[field] = float(data.get(field, 0))
                if data[field] < 0:
                    logger.error(f"Le champ {field} ne peut pas être négatif.")
                    return jsonify({'error': f'Le champ {field} ne peut pas être négatif.'}), 400
            except ValueError:
                logger.error(f"Le champ {field} doit être un nombre valide.")
                return jsonify({'error': f'Le champ {field} doit être un nombre valide.'}), 400

        # Calcul des émissions pour chaque source
        emissions = {
            'electricity': data['electricity'] * FACTORS['electricity'],
            'gasoline': data['gasoline'] * FACTORS['gasoline'],
            'diesel': data['diesel'] * FACTORS['diesel'],
            'natural_gas': data['natural_gas'] * FACTORS['natural_gas'],
            'flight': data['flight'] * FACTORS['flight']
        }
        
        # Calcul du total des émissions
        total_emissions = sum(emissions.values())

        return jsonify({
            'total_emissions': total_emissions,
            'emissions': emissions
        })

    except Exception as e:
        logger.error(f"Erreur lors du calcul: {e}")
        return jsonify({'error': 'Une erreur est survenue lors du calcul.'}), 500

@app.route('/download_excel')
def download_excel_file():
    """Route pour télécharger les données au format Excel avec graphiques natifs (Excel) dans une seconde feuille."""
    try:
        logger.debug("Début de la génération du fichier Excel.")
        # Charger les données depuis la base de données
        df = pd.read_sql_query('SELECT * FROM results WHERE user_id = ?', 
                                 get_db_connection(), params=(current_user.id,))
        if df.empty:
            logger.debug("Aucune donnée disponible pour l'Excel.")
            return "Aucune donnée disponible.", 404

        # Lire les paramètres 'graph_type' et 'activities'
        graph_type = request.args.get('graph_type', 'bar')
        activities_param = request.args.get('activities', '')
        selected_activities = activities_param.split(',') if activities_param else list(FACTORS.keys())

        # Calcul des émissions actuelles et prévisionnelles
        for act in FACTORS.keys():
            df[f'{act}_emissions'] = df[act] * FACTORS[act]
            df[f'{act}_t_plus_1'] = df[f'{act}_emissions'] * (1 - df['reduction_rate'] / 100) * (1 + df['activity_growth'] / 100)

        # Calcul du total des émissions actuelles et prévisionnelles
        df['total_emissions'] = df[[f'{act}_emissions' for act in FACTORS.keys()]].sum(axis=1)
        df['total_emissions_t_plus_1'] = df[[f'{act}_t_plus_1' for act in FACTORS.keys()]].sum(axis=1)

        # Arrondir les résultats
        df = df.round(4)

        # Supprimer les colonnes 'reduction_rate' et 'activity_growth' du fichier Excel
        df_excel = df.drop(columns=['reduction_rate', 'activity_growth'])

        # Préparer un buffer en mémoire pour l'export Excel
        output = io.BytesIO()

        # Créer un fichier Excel avec xlsxwriter
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Écrire les données dans la feuille Excel 'Données'
            df_excel.to_excel(writer, sheet_name='Données', index=False)

            # Accéder au classeur et à la feuille Excel
            workbook = writer.book
            worksheet = writer.sheets['Données']

            # Ajuster la largeur des colonnes pour bien voir les données
            worksheet.set_column('A:A', 12)  # ID column
            worksheet.set_column('B:Z', 18)  # Data columns

            # Créer une nouvelle feuille pour les graphiques
            chart_sheet = workbook.add_worksheet('Graphiques')

            # Créer le graphique selon le type sélectionné
            chart_types = {
                'bar': 'column',
                'pie': 'pie',
                'scatter': 'scatter',
                'line': 'line',
                'area': 'area',
                'radar': 'radar'  # Note: 'radar' charts are not supported by xlsxwriter
            }
            chart_type_excel = chart_types.get(graph_type, 'column')

            # Vérifier si le type de graphique est supporté par xlsxwriter
            supported_chart_types = ['column', 'pie', 'scatter', 'line', 'area']
            if chart_type_excel not in supported_chart_types:
                chart_type_excel = 'column'  # Type par défaut

            chart_ect = workbook.add_chart({'type': chart_type_excel})

            if graph_type == 'pie':
                # Pour le diagramme circulaire, Excel attend une seule série
                col_num = df_excel.columns.get_loc('total_emissions')
                chart_ect.add_series({
                    'name': 'Total Émissions (ECt)',
                    'categories': ['Données', 1, 0, len(df_excel), 0],  # IDs
                    'values': ['Données', 1, col_num, len(df_excel), col_num],
                })
            else:
                for act in selected_activities:
                    col_num = df_excel.columns.get_loc(f'{act}_emissions')
                    chart_ect.add_series({
                        'name': f"{act.capitalize()} Émissions (ECt)",
                        'categories': ['Données', 1, 0, len(df_excel), 0],  # IDs
                        'values': ['Données', 1, col_num, len(df_excel), col_num],
                    })

            # Configurer le graphique
            chart_ect.set_title({'name': 'Émissions Actuelles (ECt)'})
            chart_ect.set_x_axis({'name': 'ID'})
            chart_ect.set_y_axis({'name': 'kg CO2e'})
            chart_ect.set_style(10)

            # Insérer le graphique dans la feuille 'Graphiques'
            chart_sheet.insert_chart('B2', chart_ect)

            # Créer un second graphique pour les émissions prévisionnelles (ECt+1)
            chart_ect_plus_1 = workbook.add_chart({'type': chart_type_excel})

            if graph_type == 'pie':
                col_num = df_excel.columns.get_loc('total_emissions_t_plus_1')
                chart_ect_plus_1.add_series({
                    'name': 'Total Émissions (ECt+1)',
                    'categories': ['Données', 1, 0, len(df_excel), 0],  # IDs
                    'values': ['Données', 1, col_num, len(df_excel), col_num],
                })
            else:
                for act in selected_activities:
                    col_num = df_excel.columns.get_loc(f'{act}_t_plus_1')
                    chart_ect_plus_1.add_series({
                        'name': f"{act.capitalize()} Émissions (ECt+1)",
                        'categories': ['Données', 1, 0, len(df_excel), 0],  # IDs
                        'values': ['Données', 1, col_num, len(df_excel), col_num],
                    })

            # Configurer le graphique
            chart_ect_plus_1.set_title({'name': 'Émissions Prévisionnelles (ECt+1)'})
            chart_ect_plus_1.set_x_axis({'name': 'ID'})
            chart_ect_plus_1.set_y_axis({'name': 'kg CO2e'})
            chart_ect_plus_1.set_style(10)

            # Insérer le second graphique dans la feuille 'Graphiques'
            chart_sheet.insert_chart('B20', chart_ect_plus_1)

        # Revenir au début du buffer avant l'envoi
        output.seek(0)

        logger.debug("Fichier Excel généré avec succès.")
        # Envoyer le fichier en pièce jointe avec le bon mimetype
        return send_file(
            output,
            as_attachment=True,
            download_name='carbon_footprint_data_with_charts.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"Erreur lors du téléchargement du fichier Excel : {e}", exc_info=True)
        return f"Erreur lors du téléchargement du fichier Excel : {str(e)}", 500

@app.route('/download_pdf')
def download_pdf_file():
    """Route pour télécharger les données au format PDF avec graphiques."""
    try:
        logger.debug("Début de la génération du PDF.")
        # Charger les données depuis la base de données
        df = pd.read_sql_query('SELECT * FROM results WHERE user_id = ?', 
                                 get_db_connection(), params=(current_user.id,))
        if df.empty:
            logger.debug("Aucune donnée disponible pour le PDF.")
            return "Aucune donnée disponible.", 404

        # Lire les paramètres 'graph_type' et 'activities'
        graph_type = request.args.get('graph_type', 'bar')
        activities_param = request.args.get('activities', '')
        selected_activities = activities_param.split(',') if activities_param else list(FACTORS.keys())

        # Calcul des émissions actuelles et prévisionnelles
        logger.debug("Calcul des émissions.")
        for act in FACTORS.keys():
            df[f'{act}_emissions'] = df[act] * FACTORS[act]
            df[f'{act}_t_plus_1'] = df[f'{act}_emissions'] * (
                1 - df['reduction_rate'] / 100) * (1 + df['activity_growth'] / 100)

        df['total_emissions'] = df[[f'{act}_emissions' for act in FACTORS.keys()]].sum(axis=1)
        df['total_emissions_t_plus_1'] = df[[f'{act}_t_plus_1' for act in FACTORS.keys()]].sum(axis=1)

        df = df.round(2)
        logger.debug("Calcul des émissions terminé.")

        # Supprimer les colonnes 'reduction_rate' et 'activity_growth' du PDF
        df_pdf = df.drop(columns=['reduction_rate', 'activity_growth'])

        # Générer les graphiques avec Matplotlib
        logger.debug("Génération des graphiques avec Matplotlib.")

        # Graphique des émissions actuelles
        plt.figure(figsize=(10, 6))

        if graph_type == 'bar':
            df_plot = df_pdf[['id'] + [f'{act}_emissions' for act in selected_activities]]
            df_plot.set_index('id').plot(kind='bar', stacked=True)
            plt.title("Émissions Actuelles (ECt)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")
        elif graph_type == 'pie':
            df_plot = df_pdf[['id', 'total_emissions']]
            df_plot.set_index('id')['total_emissions'].plot(kind='pie', autopct='%1.1f%%')
            plt.title("Répartition des Émissions Actuelles (ECt)")
            plt.ylabel('')
        elif graph_type == 'scatter':
            for act in selected_activities:
                plt.scatter(df_pdf['id'], df_pdf[f'{act}_emissions'], label=act.capitalize())
            plt.title("Émissions Actuelles (ECt)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")
            plt.legend()
        elif graph_type == 'line':
            for act in selected_activities:
                plt.plot(df_pdf['id'], df_pdf[f'{act}_emissions'], marker='o', label=act.capitalize())
            plt.title("Émissions Actuelles (ECt)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")
            plt.legend()
        elif graph_type == 'area':
            df_plot = df_pdf[['id'] + [f'{act}_emissions' for act in selected_activities]]
            df_plot.set_index('id').plot(kind='area', stacked=True)
            plt.title("Émissions Actuelles (ECt)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")
        elif graph_type == 'radar':
            # Préparation des données pour le radar chart
            labels = selected_activities
            num_vars = len(labels)
            angles = [n / float(num_vars) * 2 * 3.1416 for n in range(num_vars)]
            angles += angles[:1]

            ax = plt.subplot(111, polar=True)

            for index, row in df_pdf.iterrows():
                values = [row[f'{act}_emissions'] for act in labels]
                values += values[:1]
                ax.plot(angles, values, label=f"ID {int(row['id'])}")
                ax.fill(angles, values, alpha=0.1)

            plt.title("Émissions Actuelles (ECt)")
            plt.xticks(angles[:-1], labels)
            plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
        else:
            df_plot = df_pdf[['id'] + [f'{act}_emissions' for act in selected_activities]]
            df_plot.set_index('id').plot(kind='bar', stacked=True)
            plt.title("Émissions Actuelles (ECt)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")

        plt.tight_layout()
        # Sauvegarder l'image dans un buffer
        img_bytes_ect = io.BytesIO()
        plt.savefig(img_bytes_ect, format='png')
        plt.close()
        img_bytes_ect.seek(0)
        logger.debug("Graphique des émissions actuelles généré avec succès.")

        # Graphique des émissions prévisionnelles
        plt.figure(figsize=(10, 6))

        if graph_type == 'bar':
            df_plot = df_pdf[['id'] + [f'{act}_t_plus_1' for act in selected_activities]]
            df_plot.set_index('id').plot(kind='bar', stacked=True)
            plt.title("Émissions Prévisionnelles (ECt+1)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")
        elif graph_type == 'pie':
            df_plot = df_pdf[['id', 'total_emissions_t_plus_1']]
            df_plot.set_index('id')['total_emissions_t_plus_1'].plot(kind='pie', autopct='%1.1f%%')
            plt.title("Répartition des Émissions Prévisionnelles (ECt+1)")
            plt.ylabel('')
        elif graph_type == 'scatter':
            for act in selected_activities:
                plt.scatter(df_pdf['id'], df_pdf[f'{act}_t_plus_1'], label=act.capitalize())
            plt.title("Émissions Prévisionnelles (ECt+1)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")
            plt.legend()
        elif graph_type == 'line':
            for act in selected_activities:
                plt.plot(df_pdf['id'], df_pdf[f'{act}_t_plus_1'], marker='o', label=act.capitalize())
            plt.title("Émissions Prévisionnelles (ECt+1)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")
            plt.legend()
        elif graph_type == 'area':
            df_plot = df_pdf[['id'] + [f'{act}_t_plus_1' for act in selected_activities]]
            df_plot.set_index('id').plot(kind='area', stacked=True)
            plt.title("Émissions Prévisionnelles (ECt+1)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")
        elif graph_type == 'radar':
            # Préparation des données pour le radar chart
            labels = selected_activities
            num_vars = len(labels)
            angles = [n / float(num_vars) * 2 * 3.1416 for n in range(num_vars)]
            angles += angles[:1]

            ax = plt.subplot(111, polar=True)

            for index, row in df_pdf.iterrows():
                values = [row[f'{act}_t_plus_1'] for act in labels]
                values += values[:1]
                ax.plot(angles, values, label=f"ID {int(row['id'])}")
                ax.fill(angles, values, alpha=0.1)

            plt.title("Émissions Prévisionnelles (ECt+1)")
            plt.xticks(angles[:-1], labels)
            plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
        else:
            df_plot = df_pdf[['id'] + [f'{act}_t_plus_1' for act in selected_activities]]
            df_plot.set_index('id').plot(kind='bar', stacked=True)
            plt.title("Émissions Prévisionnelles (ECt+1)")
            plt.xlabel("ID")
            plt.ylabel("kg CO2e")

        plt.tight_layout()
        # Sauvegarder l'image dans un buffer
        img_bytes_ect_plus_1 = io.BytesIO()
        plt.savefig(img_bytes_ect_plus_1, format='png')
        plt.close()
        img_bytes_ect_plus_1.seek(0)
        logger.debug("Graphique des émissions prévisionnelles généré avec succès.")

        # Création du fichier PDF avec FPDF
        logger.debug("Création du PDF.")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(left=15, top=15, right=15)

        # Page de titre
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, "Rapport d'Émissions Carbone", ln=True, align='C')

        # Afficher le tableau des émissions actuelles
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, "Émissions Actuelles (ECt):", ln=True)

        # Ajouter les données du tableau ECt dans le PDF
        pdf.set_font('Helvetica', '', 10)
        page_width = pdf.w - 2 * pdf.l_margin

        for _, row in df_pdf.iterrows():
            # Formater les données avec 2 décimales pour ECt
            row_data = f"ID: {int(row['id'])} | " + " | ".join(
                [f"{act.capitalize()} ECt: {row[f'{act}_emissions']:.2f}" for act in selected_activities]) + \
                f" | Total ECt: {row['total_emissions']:.2f}"
            pdf.multi_cell(page_width, 8, row_data)

        # Ajouter un espace avant le tableau ECt+1
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, "Émissions Prévisionnelles (ECt+1):", ln=True)

        # Ajouter les données du tableau ECt+1 dans le PDF
        pdf.set_font('Helvetica', '', 10)
        for _, row in df_pdf.iterrows():
            # Formater les données avec 2 décimales pour ECt+1
            row_data = f"ID: {int(row['id'])} | " + " | ".join(
                [f"{act.capitalize()} ECt+1: {row[f'{act}_t_plus_1']:.2f}" for act in selected_activities]) + \
                f" | Total ECt+1: {row['total_emissions_t_plus_1']:.2f}"
            pdf.multi_cell(page_width, 8, row_data)

        # Ajouter le graphique des émissions actuelles
        logger.debug("Ajout du graphique des émissions actuelles au PDF.")
        pdf.add_page()
        # Sauvegarder l'image dans un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file_ect:
            tmp_file_ect.write(img_bytes_ect.getvalue())
            tmp_file_ect_name = tmp_file_ect.name
        pdf.image(tmp_file_ect_name, x=15, y=20, w=pdf.w - 30)
        os.remove(tmp_file_ect_name)

        # Ajouter le graphique des émissions prévisionnelles
        logger.debug("Ajout du graphique des émissions prévisionnelles au PDF.")
        pdf.add_page()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file_ect_plus_1:
            tmp_file_ect_plus_1.write(img_bytes_ect_plus_1.getvalue())
            tmp_file_ect_plus_1_name = tmp_file_ect_plus_1.name
        pdf.image(tmp_file_ect_plus_1_name, x=15, y=20, w=pdf.w - 30)
        os.remove(tmp_file_ect_plus_1_name)

        # Sauvegarder le PDF en mémoire
        logger.debug("Sauvegarde du PDF en mémoire.")
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        output = io.BytesIO(pdf_bytes)

        logger.debug("PDF généré avec succès.")
        # Envoyer le fichier en pièce jointe
        return send_file(
            output,
            as_attachment=True,
            download_name='carbon_footprint_report_with_graphs.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        logger.error("Erreur lors du téléchargement du PDF", exc_info=True)
        return f"Erreur lors du téléchargement du fichier PDF : {str(e)}", 500

@app.route('/submit_results', methods=['POST'])
@login_required
def submit_results():
    electricity = request.form.get('electricity')
    gasoline = request.form.get('gasoline')
    diesel = request.form.get('diesel')
    natural_gas = request.form.get('natural_gas')
    flight = request.form.get('flight')

    # Vérifiez que les champs ne sont pas None avant de les utiliser
    if electricity is None or gasoline is None or diesel is None or natural_gas is None or flight is None:
        logger.error("Un ou plusieurs champs sont manquants.")
        return redirect(url_for('index'))  # Redirige vers la page d'index

    try:
        with sqlite3.connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO results (user_id, electricity, gasoline, diesel, natural_gas, flight) VALUES (?, ?, ?, ?, ?, ?)",
                        (current_user.id, electricity, gasoline, diesel, natural_gas, flight))
            conn.commit()
    except Exception as e:
        logger.error(f"Erreur lors de la soumission des résultats: {e}")

    return redirect(url_for('index'))  # Redirige vers la page d'index

@app.route('/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append((rule.endpoint, rule.rule))
    return render_template('routes.html', routes=routes)

# Configuration du layout Dash avec plusieurs pages
dash_app.layout = html.Div([
    # Navigation
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Accueil", href="/")),
            dbc.NavItem(dbc.NavLink("Émissions", href="/dash/emissions")),
            dbc.NavItem(dbc.NavLink("Graphiques", href="/dash/graphs")),
            dbc.NavItem(dbc.NavLink("Déconnexion", href="/logout")),
        ],
        brand="Tableau de Bord CO2",
        color="primary",
        dark=True,
    ),
    
    # Contenu principal
    html.Div([
        html.H1('Tableau de Bord des Émissions de CO2', 
                style={'textAlign': 'center', 'color': '#2c3e50', 'margin': '20px'}),
        
        # Sélecteur de graphique
        html.Div([
            html.Label('Type de graphique:'),
            dcc.Dropdown(
                id='graph-type',
                options=[
                    {'label': 'Diagramme en barres', 'value': 'bar'},
                    {'label': 'Camembert', 'value': 'pie'},
                    {'label': 'Ligne', 'value': 'line'},
                    {'label': 'Zone', 'value': 'area'}
                ],
                value='bar'
            ),
        ], style={'width': '50%', 'margin': '20px auto'}),
        
        # Graphique
        dcc.Graph(id='emissions-graph'),
        
        # Tableau récapitulatif
        html.Div([
            html.H2('Récapitulatif des émissions', 
                   style={'textAlign': 'center', 'margin': '20px'}),
            dash_table.DataTable(
                id='emissions-table',
                style_table={'margin': '20px'},
                style_cell={'textAlign': 'center'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
        ])
    ], style={'padding': '20px'})
])

# Callbacks Dash
@dash_app.callback(
    [Output('emissions-graph', 'figure'),
     Output('emissions-table', 'data'),
     Output('emissions-table', 'columns')],
    [Input('graph-type', 'value')]
)
def update_dashboard(graph_type):
    try:
        conn = get_db_connection()
        df = pd.read_sql_query('SELECT * FROM results WHERE user_id = ?', 
                              conn, params=(current_user.id,))
        conn.close()

        if df.empty:
            return {}, [], []

        # Inverser l'ordre des lignes du DataFrame
        df = df[::-1]  # Inverser le DataFrame

        # Calcul des émissions pour chaque source
        for act in FACTORS.keys():
            df[f'{act}_emissions'] = df[act] * FACTORS[act]

        # Calcul du total des émissions
        df['total_emissions'] = df[[f'{act}_emissions' for act in FACTORS.keys()]].sum(axis=1)

        # Supprimer les colonnes 'reduction_rate' et 'activity_growth'
        df = df.drop(columns=['reduction_rate', 'activity_growth'])

        # Réorganiser les colonnes pour mettre les colonnes de consommation à côté de leurs émissions
        cols = []
        for act in FACTORS.keys():
            cols.append(act)  # Ajoute la colonne de consommation
            cols.append(f'{act}_emissions')  # Ajoute la colonne d'émissions

        # Ajouter 'id' et 'user_id' au début et 'total_emissions' à la fin
        cols = ['id', 'user_id'] + cols + ['total_emissions']
        df = df[cols]

        # Création du graphique
        fig = px.bar(df, 
                     x='id',
                     y=[f'{act}_emissions' for act in FACTORS.keys()],
                     title='Émissions de CO2 par source',
                     labels={'value': 'kg CO2e', 'variable': 'Source'})

        # Préparation des données pour le tableau
        table_data = df.to_dict('records')
        columns = [{"name": i, "id": i} for i in df.columns]

        return fig, table_data, columns

    except Exception as e:
        print(f"Erreur lors de la mise à jour du dashboard: {e}")
        return {}, [], []


if __name__ == '__main__':
    logger.info("Démarrage de l'application.")
    app.run(debug=True, port=5000)
