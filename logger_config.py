import logging
import logging.handlers
import os
from datetime import datetime

# Création du dossier logs s'il n'existe pas
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configuration du format des logs
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_logger():
    # Création du logger principal
    logger = logging.getLogger('carbon_footprint')
    logger.setLevel(logging.DEBUG)

    # Handler pour les logs de debug dans un fichier
    debug_handler = logging.handlers.RotatingFileHandler(
        filename='logs/debug.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(log_format)

    # Handler pour les logs d'erreur dans un fichier séparé
    error_handler = logging.handlers.RotatingFileHandler(
        filename='logs/error.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)

    # Handler pour les logs d'authentification
    auth_handler = logging.handlers.RotatingFileHandler(
        filename='logs/auth.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    auth_handler.setLevel(logging.INFO)
    auth_handler.setFormatter(log_format)

    # Handler pour afficher les logs dans la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)

    # Handler pour les accès HTTP
    http_handler = logging.handlers.TimedRotatingFileHandler(
        filename='logs/access.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    http_handler.setLevel(logging.INFO)
    http_handler.setFormatter(log_format)

    # Suppression des handlers existants
    logger.handlers = []

    # Ajout des handlers au logger
    logger.addHandler(debug_handler)
    logger.addHandler(error_handler)
    logger.addHandler(auth_handler)
    logger.addHandler(console_handler)
    logger.addHandler(http_handler)

    # Création de loggers spécifiques
    loggers = {
        'auth': logging.getLogger('carbon_footprint.auth'),
        'db': logging.getLogger('carbon_footprint.db'),
        'api': logging.getLogger('carbon_footprint.api'),
        'dashboard': logging.getLogger('carbon_footprint.dashboard')
    }

    for log_name, log_instance in loggers.items():
        log_instance.handlers = []
        log_instance.propagate = True
        log_instance.setLevel(logging.DEBUG)

    return logger, loggers

# Fonction pour journaliser les requêtes HTTP
def log_request(response):
    from flask import request
    logger = logging.getLogger('carbon_footprint.api')
    logger.info(
        f'{request.remote_addr} - "{request.method} {request.full_path}" '
        f'{response.status_code}'
    )
    return response

# Fonction pour journaliser les erreurs
def log_error(error):
    from flask import request
    logger = logging.getLogger('carbon_footprint')
    logger.error(
        f'Error: {str(error)} - Route: {request.url} - '
        f'Method: {request.method} - IP: {request.remote_addr}'
    )

# Configuration des niveaux de log selon l'environnement
def configure_log_levels(env):
    levels = {
        'development': logging.DEBUG,
        'testing': logging.INFO,
        'production': logging.WARNING
    }
    return levels.get(env, logging.DEBUG)