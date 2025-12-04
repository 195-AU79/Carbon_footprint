# Calculateur d'Empreinte Carbone

Application web Flask/Dash pour calculer et visualiser votre empreinte carbone personnelle. Cette application permet de suivre vos émissions de CO2 provenant de différentes sources et de générer des rapports détaillés.

## 🚀 Fonctionnalités

- **Authentification utilisateur** : Système de connexion/inscription sécurisé avec Flask-Login
- **Calcul d'empreinte carbone** : Calcul automatique des émissions CO2e pour :
  - Électricité (kWh)
  - Essence (litres)
  - Diesel (litres)
  - Gaz naturel (m³)
  - Vols (km)
- **Tableau de bord interactif** : Visualisation des données avec Dash/Plotly
- **Export de données** : Téléchargement des résultats en format Excel ou PDF avec graphiques
- **Historique des calculs** : Suivi de vos calculs précédents
- **Système de logs** : Journalisation complète des activités

## 📋 Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## 🔧 Installation

### 1. Cloner ou télécharger le projet

```bash
cd Carbon_footprint-main
```

### 2. Créer un environnement virtuel (recommandé)

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

**Note :** Si Flask n'est pas installé, ajoutez-le :
```bash
pip install Flask
```

### 4. Initialiser la base de données

**Important :** Vous devez créer la base de données avant de lancer l'application.

```bash
python init_db.py
```

Cette commande crée le fichier `carbon_footprint.db` avec les tables nécessaires (`user` et `results`).

### 5. (Optionnel) Créer un utilisateur de test

```bash
python create_user.py
```

Suivez les instructions pour créer un compte utilisateur avec :
- Nom d'utilisateur
- Mot de passe
- Email

## 🏃 Démarrage de l'application

Une fois la base de données initialisée, lancez l'application :

```bash
python app11.py
```

L'application sera accessible à l'adresse : **http://localhost:5000**

## 📖 Utilisation

### Première utilisation

1. **Créer un compte** :
   - Cliquez sur "S'inscrire" ou accédez à `/register`
   - Remplissez le formulaire avec votre nom d'utilisateur, email et mot de passe
   - Cliquez sur "S'inscrire"

2. **Se connecter** :
   - Accédez à `/login` ou utilisez le formulaire de connexion
   - Entrez vos identifiants
   - Cliquez sur "Se connecter"

3. **Saisir vos données** :
   - Une fois connecté, remplissez le formulaire avec vos consommations :
     - **Électricité** : consommation en kWh
     - **Essence** : consommation en litres
     - **Diesel** : consommation en litres
     - **Gaz naturel** : consommation en m³
     - **Vol** : distance parcourue en km
   - Cliquez sur "Soumettre les résultats"

4. **Visualiser vos résultats** :
   - Vos résultats s'affichent sur la page d'accueil
   - Accédez au tableau de bord interactif via `/dash/`

### Tableau de bord Dash

- Accédez à `/dash/` pour voir le tableau de bord interactif
- Changez le type de graphique (barres, camembert, ligne, zone)
- Consultez le récapitulatif des émissions dans le tableau

### Export de données

- **Excel** : Cliquez sur "Télécharger les données au format Excel"
  - Génère un fichier `.xlsx` avec deux feuilles :
    - Feuille "Données" : toutes vos données
    - Feuille "Graphiques" : graphiques Excel natifs
  
- **PDF** : Cliquez sur "Télécharger les données au format PDF"
  - Génère un rapport PDF avec :
    - Tableaux des émissions actuelles (ECt)
    - Tableaux des émissions prévisionnelles (ECt+1)
    - Graphiques des émissions

### Déconnexion

- Cliquez sur "Déconnexion" ou accédez à `/logout`

## 📁 Structure du projet

```
Carbon_footprint/
├── app11.py              # Application principale Flask/Dash
├── init_db.py            # Script d'initialisation de la base de données
├── create_user.py        # Script pour créer un utilisateur manuellement
├── logger_config.py      # Configuration du système de logs
├── requirements.txt      # Dépendances Python
├── carbon_footprint.db   # Base de données SQLite (créée après init_db.py)
├── logs/                 # Dossier des fichiers de logs
│   ├── access.log       # Logs d'accès HTTP
│   ├── auth.log         # Logs d'authentification
│   ├── debug.log        # Logs de débogage
│   └── error.log        # Logs d'erreurs
├── static/               # Fichiers statiques (CSS, JS)
│   └── style.css
└── templates/            # Templates HTML
    ├── base.html
    ├── index.html        # Page d'accueil avec formulaire
    ├── login.html        # Page de connexion
    ├── register.html     # Page d'inscription
    └── 404.html          # Page d'erreur 404
```

## 🔐 Facteurs d'émission

L'application utilise les facteurs d'émission suivants (kg CO2e par unité) :

| Source | Facteur d'émission |
|--------|-------------------|
| Électricité | 0.05 kg CO2e/kWh |
| Essence | 2.31 kg CO2e/litre |
| Diesel | 2.68 kg CO2e/litre |
| Gaz naturel | 2.75 kg CO2e/m³ |
| Vol | 0.115 kg CO2e/km |

## 🛠️ Technologies utilisées

- **Flask** : Framework web Python
- **Dash** : Framework pour tableaux de bord interactifs
- **SQLAlchemy** : ORM pour la gestion de la base de données
- **SQLite** : Base de données relationnelle légère
- **Plotly** : Visualisation de données interactives
- **Pandas** : Manipulation et analyse de données
- **Matplotlib** : Génération de graphiques pour PDF
- **FPDF** : Génération de fichiers PDF
- **XlsxWriter** : Génération de fichiers Excel avec graphiques
- **Flask-Login** : Gestion de l'authentification utilisateur
- **Werkzeug** : Utilitaires de sécurité (hashage des mots de passe)

## 🐛 Dépannage

### Erreur : "La base de données carbon_footprint.db n'existe pas"

**Solution :** Exécutez d'abord `python init_db.py` pour créer la base de données avant de lancer l'application.

### Erreur : "Module not found" ou "No module named 'flask'"

**Solution :** 
1. Vérifiez que votre environnement virtuel est activé
2. Installez toutes les dépendances : `pip install -r requirements.txt`
3. Si Flask manque, installez-le : `pip install Flask`

### Erreur : Port 5000 déjà utilisé

**Solution :** Modifiez le port dans `app11.py` (ligne 844) :
```python
app.run(debug=True, port=5001)  # Changez 5000 en 5001 ou un autre port disponible
```

### Erreur lors de la connexion à la base de données

**Solution :** 
1. Vérifiez que `carbon_footprint.db` existe dans le répertoire du projet
2. Réinitialisez la base de données en supprimant `carbon_footprint.db` et en relançant `init_db.py`
3. Vérifiez les permissions d'accès au fichier

### Erreur lors de l'inscription/connexion

**Solution :**
- Assurez-vous que la base de données a été correctement initialisée
- Vérifiez que les tables `user` et `results` existent
- Consultez les logs dans le dossier `logs/` pour plus de détails

## 📝 Notes importantes

- **Base de données** : La base de données est stockée localement dans le fichier `carbon_footprint.db`
- **Sécurité** : Les mots de passe sont hashés avec `pbkdf2:sha256` via Werkzeug
- **Logs** : Tous les logs sont enregistrés dans le dossier `logs/` avec rotation automatique
- **Mode debug** : L'application fonctionne en mode debug par défaut (désactivez-le en production)
- **Données utilisateur** : Chaque utilisateur ne voit que ses propres données (filtrage par `user_id`)

## 🔒 Sécurité

- Les mots de passe sont hashés avant stockage
- Les sessions utilisateur sont gérées par Flask-Login
- Les routes protégées nécessitent une authentification
- La clé secrète Flask doit être changée en production

## 📄 Routes disponibles

- `/` : Page d'accueil (nécessite authentification)
- `/login` : Page de connexion
- `/register` : Page d'inscription
- `/logout` : Déconnexion
- `/dash/` : Tableau de bord Dash (nécessite authentification)
- `/calculate` : API pour calculer les émissions (POST, nécessite authentification)
- `/submit_results` : Soumettre des résultats (POST, nécessite authentification)
- `/download_excel` : Télécharger les données en Excel (nécessite authentification)
- `/download_pdf` : Télécharger les données en PDF (nécessite authentification)

## 👤 Auteur

Projet développé pour le calcul et le suivi de l'empreinte carbone personnelle.

## 📄 Licence

Ce projet est fourni tel quel pour un usage éducatif et personnel.

---

**Bon calcul de votre empreinte carbone ! 🌱**

Pour toute question ou problème, consultez les logs dans le dossier `logs/` pour plus d'informations.

