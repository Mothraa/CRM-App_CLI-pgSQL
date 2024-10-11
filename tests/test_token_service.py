import jwt
import pytest

from datetime import timedelta
# from jwt import ExpiredSignatureError, InvalidTokenError
from my_app.services.token_service import TokenManager

# TODO ajouter des tests liés a un mauvais param (mauvais algo, absence secret_key, lifetime négatif,...)


@pytest.fixture
def token_manager_fixture(monkeypatch):
    """Fixture to initialize TokenManager with mock configurations."""
    monkeypatch.setattr("os.getenv", lambda key: "fake_secret_key" if key == "SECRET_KEY" else None)

    # creation d'une instance
    token_manager = TokenManager()

    # surcharge de la configuration
    token_manager.SECRET_KEY = "fake_secret_key"
    token_manager.ALGORITHMS = "HS256"
    token_manager.ACCESS_TOKEN_LIFETIME = 10  # minutes
    token_manager.REFRESH_TOKEN_LIFETIME = 720  # minutes
    token_manager.TIME_ZONE_NAME = "Europe/Paris"

    return token_manager


@pytest.mark.unit
def test_generate_access_token(token_manager_fixture, monkeypatch, mock_time, mock_user):
    """Tests the generation of an access token for a user with a fake frozen time"""

    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            if tz:
                return mock_time.astimezone(tz)  # utilise la timezone si indiqué
            return mock_time

    monkeypatch.setattr("datetime.datetime", MockDateTime)
    monkeypatch.setattr("my_app.services.token_service.datetime", MockDateTime)

    # utilisation de l'id du mock_user pour générer un token
    token = token_manager_fixture.generate_access_token(mock_user.id)

    # décodage du token avec le temps figé également
    monkeypatch.setattr("jwt.api_jwt.datetime", MockDateTime)

    decoded_token = jwt.decode(token, token_manager_fixture.SECRET_KEY, algorithms=[token_manager_fixture.ALGORITHMS])

    assert decoded_token["user_id"] == mock_user.id
    assert decoded_token["type"] == "access"
    assert decoded_token["iat"] == int(mock_time.timestamp())
    assert decoded_token["exp"] == int((mock_time + timedelta(minutes=token_manager_fixture.ACCESS_TOKEN_LIFETIME))
                                       .timestamp())


@pytest.mark.unit
def test_generate_refresh_token(token_manager_fixture, monkeypatch, mock_time, mock_user):
    """tests the generation of an refresh token for a user with a fake frozen time"""

    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            if tz:
                return mock_time.astimezone(tz)  # utilise la timezone si indiqué
            return mock_time

    monkeypatch.setattr("datetime.datetime", MockDateTime)
    monkeypatch.setattr("my_app.services.token_service.datetime", MockDateTime)

    # utilisation de l'id du mock_user pour générer un token
    token = token_manager_fixture.generate_refresh_token(mock_user.id)

    # décodage du token avec le temps figé également
    monkeypatch.setattr("jwt.api_jwt.datetime", MockDateTime)

    decoded_token = jwt.decode(token, token_manager_fixture.SECRET_KEY, algorithms=[token_manager_fixture.ALGORITHMS])

    assert decoded_token["user_id"] == mock_user.id
    assert decoded_token["type"] == "refresh"
    assert decoded_token["iat"] == int(mock_time.timestamp())
    assert decoded_token["exp"] == int((mock_time + timedelta(minutes=token_manager_fixture.REFRESH_TOKEN_LIFETIME))
                                       .timestamp())


@pytest.mark.unit
def test_verify_token_method(token_manager_fixture, mock_user, mock_time):
    """tests the validation of a valid token (verify_token method)"""
    # Access token test
    access_token = token_manager_fixture.generate_access_token(mock_user.id)
    decoded_access_payload = token_manager_fixture.verify_token(access_token)
    refresh_token = token_manager_fixture.generate_refresh_token(mock_user.id)
    decoded_refresh_payload = token_manager_fixture.verify_token(refresh_token)

    assert decoded_access_payload["user_id"] == mock_user.id
    assert decoded_access_payload["type"] == "access"
    assert decoded_refresh_payload["user_id"] == mock_user.id
    assert decoded_refresh_payload["type"] == "refresh"


@pytest.mark.unit
def test_verify_token_expired(token_manager_fixture, mock_user, mock_time):
    """tests the validation of an expired token (verify_token method)"""
    expired_token = jwt.encode({
        "user_id": mock_user.id,
        "exp": mock_time - timedelta(minutes=1),  # token expiré il y a 1 min
        "iat": mock_time - timedelta(minutes=11),  # token généré il y a 11 min
        "type": "access"
    }, token_manager_fixture.SECRET_KEY, algorithm=token_manager_fixture.ALGORITHMS)

    decoded_payload = token_manager_fixture.verify_token(expired_token)
    # TODO : ajouter des exceptions
    assert decoded_payload is None


@pytest.mark.unit
def test_refresh_access_token_invalid(token_manager_fixture):
    """tests an invalid refresh token"""
    invalid_token = "fake.invalid.token"

    new_access_token = token_manager_fixture.refresh_access_token(invalid_token)

    assert new_access_token is None


@pytest.mark.unit
def test_verify_token_invalid(token_manager_fixture):
    """tests the validation of an invalid token (verify_token method)"""
    invalid_token = "fake.invalid.token"

    decoded_payload = token_manager_fixture.verify_token(invalid_token)

    assert decoded_payload is None


@pytest.mark.unit
def test_refresh_access_token_valid(token_manager_fixture, monkeypatch, mock_user, mock_time):
    """Tests the creation of a new access token from a refresh token"""

    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            if tz:
                return mock_time.astimezone(tz)  # utilise la timezone si indiqué
            return mock_time

    # remplace datetime dans le module token_service et jwt
    monkeypatch.setattr("datetime.datetime", MockDateTime)
    monkeypatch.setattr("my_app.services.token_service.datetime", MockDateTime)
    monkeypatch.setattr("jwt.api_jwt.datetime", MockDateTime)

    refresh_token = token_manager_fixture.generate_refresh_token(mock_user.id)

    new_access_token = token_manager_fixture.refresh_access_token(refresh_token)
    decoded_access_token = jwt.decode(new_access_token, token_manager_fixture.SECRET_KEY, algorithms=[token_manager_fixture.ALGORITHMS])

    assert decoded_access_token["user_id"] == mock_user.id
    assert decoded_access_token["type"] == "access"
    assert decoded_access_token["iat"] == int(mock_time.timestamp())
    assert decoded_access_token["exp"] == int((mock_time + timedelta(minutes=token_manager_fixture.ACCESS_TOKEN_LIFETIME))
                                              .timestamp())


@pytest.mark.unit
def test_refresh_access_token_expired(token_manager_fixture, mock_user, mock_time):
    """Tests the creation of a new access token from an expired refresh token."""
    expired_refresh_token = jwt.encode({
        "user_id": mock_user.id,
        "exp": mock_time - timedelta(minutes=1),  # token expiré il y a 1 min
        "iat": mock_time - timedelta(minutes=721),  # token généré il y a 12h et 1 min
        "type": "refresh"
    }, token_manager_fixture.SECRET_KEY, algorithm=token_manager_fixture.ALGORITHMS)

    new_access_token = token_manager_fixture.refresh_access_token(expired_refresh_token)

    assert new_access_token is None
