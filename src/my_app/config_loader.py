import os
import yaml
import pytz

from dotenv import load_dotenv

# chargement du nom du schema depuis l'environnement (.env)
load_dotenv()
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")

# récupération de la time_zone depuis le fichier config.yaml
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
    TIME_ZONE_NAME = config['global']['TIME_ZONE']
    TIME_ZONE = pytz.timezone(TIME_ZONE_NAME)

    TOKEN_ALGORITHMS = config['jwt']['TOKEN_ALGORITHMS']
    ACCESS_TOKEN_LIFETIME = config['jwt']['ACCESS_TOKEN_LIFETIME']  # en minutes
    REFRESH_TOKEN_LIFETIME = config['jwt']['REFRESH_TOKEN_LIFETIME']  # en minutes
