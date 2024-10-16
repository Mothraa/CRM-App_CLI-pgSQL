from datetime import datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from my_app.config_loader import (SECRET_KEY, TIME_ZONE,
                                TOKEN_ALGORITHMS, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME
                                )


class TokenManager:
    """Manages the creation, update and verification of JWT tokens"""

    SECRET_KEY = None
    timezone = None
    TOKEN_ALGORITHMS = None
    ACCESS_TOKEN_LIFETIME = None
    REFRESH_TOKEN_LIFETIME = None

    def __init__(self):
        """Initializes TokenManager with configuration settings."""
        self.SECRET_KEY = SECRET_KEY

        self.timezone = TIME_ZONE

        self.TOKEN_ALGORITHMS = TOKEN_ALGORITHMS
        self.ACCESS_TOKEN_LIFETIME = ACCESS_TOKEN_LIFETIME
        self.REFRESH_TOKEN_LIFETIME = REFRESH_TOKEN_LIFETIME

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
        access_token = jwt.encode(access_payload, self.SECRET_KEY, algorithm=self.TOKEN_ALGORITHMS)

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
        refresh_token = jwt.encode(refresh_payload, self.SECRET_KEY, algorithm=self.TOKEN_ALGORITHMS)

        return refresh_token

    def verify_token(self, token):
        """Verify the JWT token (access or refresh)"""
        try:
            decoded_payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.TOKEN_ALGORITHMS])
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
            decoded_refresh_token = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.TOKEN_ALGORITHMS])

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
