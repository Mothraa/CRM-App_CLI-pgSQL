import os
import yaml
import pytz

from dotenv import load_dotenv

# chemin vers config.yaml à la racine du projet
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_path = os.path.join(base_dir, "config.yaml")

# chargement des informations de connexion pgsql depuis l'environnement (.env)
load_dotenv(override=True)
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")
SSL_MODE = os.getenv("SSL_MODE")
DATABASE_APP_USER = os.getenv("DATABASE_APP_USER")
DATABASE_APP_PASSWORD = os.getenv("DATABASE_APP_PASSWORD")

SECRET_KEY = os.getenv("SECRET_KEY")

# récupération des paramètres pour les tokens depuis le fichier config.yaml
with open(config_path, "r") as config_file:
    config = yaml.safe_load(config_file)

    # paramètres de debug
    DEBUG_MODE = config["global"]["DEBUG_MODE"]

    TIME_ZONE_NAME = config["global"]["TIME_ZONE"]
    TIME_ZONE = pytz.timezone(TIME_ZONE_NAME)

    TOKEN_ALGORITHMS = config["jwt"]["TOKEN_ALGORITHMS"]
    ACCESS_TOKEN_LIFETIME = config["jwt"]["ACCESS_TOKEN_LIFETIME"]  # en minutes
    REFRESH_TOKEN_LIFETIME = config["jwt"]["REFRESH_TOKEN_LIFETIME"]  # en minutes