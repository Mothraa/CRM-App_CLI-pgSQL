import jwt
import pytest

from datetime import timedelta
# from jwt import ExpiredSignatureError, InvalidTokenError
from my_app.services.auth_service import (generate_access_token,
                                          generate_refresh_token,
                                          verify_token,
                                          refresh_access_token,
                                          )

# note : données non mockées issues de .env
SECRET_KEY = "fake_secret_key"
# note : données non mockées issues de config.yaml
TIME_ZONE = "Europe/Paris"
ACCESS_TOKEN_LIFETIME = 10  # minutes
REFRESH_TOKEN_LIFETIME = 720  # minutes
ALGORITHMS = "HS256"

# TODO ajouter des tests liés a un mauvais param (mauvais algo, absence secret_key, lifetime négatif,...)


@pytest.mark.unit
def test_generate_access_token(monkeypatch, mock_time, mock_user):
    """Tests the generation of an access token for a user with a fake frozen time"""

    # surcharge avec les mocks
    monkeypatch.setattr("my_app.services.auth_service.SECRET_KEY", "fake_secret_key")
    monkeypatch.setattr("my_app.services.auth_service.ALGORITHMS", "HS256")

    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            if tz:
                return mock_time.astimezone(tz)  # utilise la timezone si indiqué
            return mock_time

    monkeypatch.setattr("my_app.services.auth_service.datetime", MockDateTime)

    # utilisation de l'id du mock_user pour générer un token
    token = generate_access_token(mock_user.id)

    # décodage du token avec le temps figé également
    monkeypatch.setattr("jwt.api_jwt.datetime", MockDateTime)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHMS])

    assert decoded_token["user_id"] == mock_user.id
    assert decoded_token["type"] == "access"
    assert decoded_token["iat"] == int(mock_time.timestamp())
    assert decoded_token["exp"] == int((mock_time + timedelta(minutes=ACCESS_TOKEN_LIFETIME)).timestamp())


@pytest.mark.unit
def test_generate_refresh_token(monkeypatch, mock_time, mock_user):
    """tests the generation of an refresh token for a user with a fake frozen time"""
    # Surcharge avec les mocks
    monkeypatch.setattr("my_app.services.auth_service.SECRET_KEY", "fake_secret_key")
    monkeypatch.setattr("my_app.services.auth_service.ALGORITHMS", "HS256")

    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            if tz:
                return mock_time.astimezone(tz)  # utilise la timezone si indiqué
            return mock_time

    monkeypatch.setattr("my_app.services.auth_service.datetime", MockDateTime)

    # utilisation de l'id du mock_user pour générer un token
    token = generate_refresh_token(mock_user.id)

    # décodage du token avec le temps figé également
    monkeypatch.setattr("jwt.api_jwt.datetime", MockDateTime)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHMS])

    assert decoded_token["user_id"] == mock_user.id
    assert decoded_token["type"] == "refresh"
    assert decoded_token["iat"] == int(mock_time.timestamp())
    assert decoded_token["exp"] == int((mock_time + timedelta(minutes=REFRESH_TOKEN_LIFETIME)).timestamp())


@pytest.mark.unit
def test_verify_token_method(mock_user, mock_time):
    """tests the validation of a valid token (verify_token method)"""
    # Access token test
    access_token = generate_access_token(mock_user.id)
    decoded_access_payload = verify_token(access_token)
    refresh_token = generate_refresh_token(mock_user.id)
    decoded_refresh_payload = verify_token(refresh_token)

    assert decoded_access_payload["user_id"] == mock_user.id
    assert decoded_access_payload["type"] == "access"
    assert decoded_refresh_payload["user_id"] == mock_user.id
    assert decoded_refresh_payload["type"] == "refresh"


@pytest.mark.unit
def test_verify_token_expired(mock_user, mock_time):
    """tests the validation of an expired token (verify_token method)"""
    expired_token = jwt.encode({
        "user_id": mock_user.id,
        "exp": mock_time - timedelta(minutes=1),  # token expiré il y a 1 min
        "iat": mock_time - timedelta(minutes=11),  # token généré il y a 11 min
        "type": "access"
    }, SECRET_KEY, algorithm=ALGORITHMS)

    decoded_payload = verify_token(expired_token)
    # TODO : ajouter des exceptions
    assert decoded_payload is None


@pytest.mark.unit
def test_refresh_access_token_invalid():
    """tests an invalid refresh token"""
    invalid_token = "fake.invalid.token"

    new_access_token = refresh_access_token(invalid_token)

    assert new_access_token is None


@pytest.mark.unit
def test_verify_token_invalid():
    """tests the validation of an invalid token (verify_token method)"""
    invalid_token = "fake.invalid.token"

    decoded_payload = verify_token(invalid_token)

    assert decoded_payload is None


@pytest.mark.unit
def test_refresh_access_token_valid(monkeypatch, mock_user, mock_time):
    """Tests the creation of a new access token from a refresh token"""
    # Surcharge des mocks
    monkeypatch.setattr("my_app.services.auth_service.SECRET_KEY", "fake_secret_key")
    monkeypatch.setattr("my_app.services.auth_service.ALGORITHMS", "HS256")

    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            if tz:
                return mock_time.astimezone(tz)  # utilise la timezone si indiqué
            return mock_time

    # remplace datetime dans le module auth_service et jwt
    monkeypatch.setattr("my_app.services.auth_service.datetime", MockDateTime)
    monkeypatch.setattr("jwt.api_jwt.datetime", MockDateTime)

    refresh_token = generate_refresh_token(mock_user.id)

    new_access_token = refresh_access_token(refresh_token)
    decoded_access_token = jwt.decode(new_access_token, SECRET_KEY, algorithms=[ALGORITHMS])

    assert decoded_access_token["user_id"] == mock_user.id
    assert decoded_access_token["type"] == "access"
    assert decoded_access_token["iat"] == int(mock_time.timestamp())
    assert decoded_access_token["exp"] == int((mock_time + timedelta(minutes=ACCESS_TOKEN_LIFETIME)).timestamp())


@pytest.mark.unit
def test_refresh_access_token_expired(mock_user, mock_time):
    """Tests the creation of a new access token from an expired refresh token."""
    expired_refresh_token = jwt.encode({
        "user_id": mock_user.id,
        "exp": mock_time - timedelta(minutes=1),  # token expiré il y a 1 min
        "iat": mock_time - timedelta(minutes=721),  # token généré il y a 12h et 1 min
        "type": "refresh"
    }, SECRET_KEY, algorithm=ALGORITHMS)

    new_access_token = refresh_access_token(expired_refresh_token)

    assert new_access_token is None
