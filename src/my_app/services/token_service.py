import os
from datetime import datetime, timedelta
import pytz

import jwt
import yaml
from jwt import ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv


class TokenManager:
    """Manages the creation, update and verification of JWT tokens"""

    SECRET_KEY = None
    timezone = None
    ALGORITHMS = None
    ACCESS_TOKEN_LIFETIME = None
    REFRESH_TOKEN_LIFETIME = None

    def __init__(self):
        """Initializes TokenManager with configuration settings."""
        load_dotenv()
        self.SECRET_KEY = os.getenv('SECRET_KEY')

        # On charge la configuration depuis config.yaml
        with open("config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)

        TIME_ZONE_NAME = config['global']['TIME_ZONE']
        self.timezone = pytz.timezone(TIME_ZONE_NAME)

        self.ALGORITHMS = config['jwt']['ALGORITHMS']
        self.ACCESS_TOKEN_LIFETIME = config['jwt']['ACCESS_TOKEN_LIFETIME']  # en minutes
        self.REFRESH_TOKEN_LIFETIME = config['jwt']['REFRESH_TOKEN_LIFETIME']  # en minutes

    def generate_access_token(self, user_id):
        """Generate an access token for one user"""
        now = datetime.now(self.timezone)
        access_payload = {
            "user_id": user_id,
            # date/heure d'expiration du token
            'exp': int((now + timedelta(minutes=self.ACCESS_TOKEN_LIFETIME)).timestamp()),
            # date/heure de création du token
            'iat': int(now.timestamp()),
            "type": "access"
        }
        access_token = jwt.encode(access_payload, self.SECRET_KEY, algorithm=self.ALGORITHMS)

        return access_token

    def generate_refresh_token(self, user_id):
        """Generate a refresh token for one user"""
        now = datetime.now(self.timezone)
        refresh_payload = {
            'user_id': user_id,
            # date/heure d'expiration du token
            'exp': int((now + timedelta(minutes=self.REFRESH_TOKEN_LIFETIME)).timestamp()),
            # date/heure de création du token
            'iat': int(now.timestamp()),
            'type': 'refresh'
        }
        refresh_token = jwt.encode(refresh_payload, self.SECRET_KEY, algorithm=self.ALGORITHMS)

        return refresh_token

    def verify_token(self, token):
        """Verify the JWT token (access or refresh)"""
        try:
            decoded_payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHMS])
            return decoded_payload
        except ExpiredSignatureError:
            print("Le token a expiré")
            return None
        except InvalidTokenError:
            print("Token invalide")
            return None

    def refresh_access_token(self, refresh_token):
        """Generate a new access token if the refresh token is valid"""
        try:
            decoded_refresh_token = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHMS])

            # On vérifie que c'est bien un refresh token
            if decoded_refresh_token.get('type') != 'refresh':
                print("Le token fourni n'est pas un refresh token.")
                return None

            user_id = decoded_refresh_token['user_id']

            # On génère un nouveau access token
            new_access_token = self.generate_access_token(user_id)
            return new_access_token
        except ExpiredSignatureError:
            print("Le refresh token a expiré")
            return None
        except InvalidTokenError:
            print("Refresh token invalide")
            return None
