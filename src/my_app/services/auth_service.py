import os
from datetime import datetime, timedelta
import pytz

import jwt
import yaml
from jwt import ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

# Charge la configuration depuis config.yaml
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

TIME_ZONE = config['global']['TIME_ZONE']
ALGORITHMS = config['jwt']['ALGORITHMS']
ACCESS_TOKEN_LIFETIME = config['jwt']['ACCESS_TOKEN_LIFETIME']  # en minutes
REFRESH_TOKEN_LIFETIME = config['jwt']['REFRESH_TOKEN_LIFETIME']  # en minutes

timezone = pytz.timezone(TIME_ZONE)


def generate_access_token(user_id):
    """Generate an access token for one user"""
    now = datetime.now(timezone)

    access_payload = {
        "user_id": user_id,
        'exp': int((now + timedelta(minutes=ACCESS_TOKEN_LIFETIME)).timestamp()),  # date/heure d'expiration du token
        'iat': int(now.timestamp()),  # date/heure de création du token
        "type": "access"
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHMS)

    return access_token


def generate_refresh_token(user_id):
    """Generate a refresh token for one user"""
    now = datetime.now(timezone)

    refresh_payload = {
        'user_id': user_id,
        'exp': int((now + timedelta(minutes=REFRESH_TOKEN_LIFETIME)).timestamp()),  # date/heure d'expiration du token
        'iat': int(now.timestamp()),  # date/heure de création du token
        'type': 'refresh'
    }
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHMS)

    return refresh_token


def verify_token(token):
    """Verify the JWT token (access or refresh)"""
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHMS])
        return decoded_payload
    except ExpiredSignatureError:
        print("Le token a expiré")
        return None
    except InvalidTokenError:
        print("Token invalide")
        return None


def refresh_access_token(refresh_token):
    """Generate a new access token if the refresh token is valid"""
    try:
        decoded_refresh_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHMS])

        # On vérifie que c'est bien un refresh token
        if decoded_refresh_token.get('type') != 'refresh':
            print("Le token fourni n'est pas un refresh token.")
            return None

        user_id = decoded_refresh_token['user_id']

        # On génère un nouveau access token
        new_access_token = generate_access_token(user_id)
        return new_access_token
    except ExpiredSignatureError:
        print("Le refresh token a expiré")
        return None
    except InvalidTokenError:
        print("Refresh token invalide")
        return None
