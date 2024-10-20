import pytest
# from my_app.controllers.main_controller import MainController
from my_app.dependencies import init_main_controller
from my_app.exceptions import AuthenticationError


@pytest.fixture
def main_controller(mock_session):
    """mock of MainController through dependencies.init_main_controller"""
    return init_main_controller(mock_session)


# Test de l'authentification réussie
def test_authenticate_user_controller_OK(main_controller, monkeypatch, mock_user):
    # Mock des méthodes du service utilisateur et du gestionnaire de tokens
    def mock_authenticate_user(email, password):
        return mock_user

    def mock_generate_access_token(user_id):
        return "access_token"

    def mock_generate_refresh_token(user_id):
        return "refresh_token"

    def mock_save_tokens(access_token, refresh_token):
        pass

    # on remplace les methodes avec monkeypatch
    monkeypatch.setattr(main_controller.user_service, "authenticate_user", mock_authenticate_user)
    monkeypatch.setattr(main_controller.token_manager, "generate_access_token", mock_generate_access_token)
    monkeypatch.setattr(main_controller.token_manager, "generate_refresh_token", mock_generate_refresh_token)
    monkeypatch.setattr(main_controller.token_manager, "save_tokens", mock_save_tokens)

    result = main_controller.authenticate_user_controller("test@example.com", "password")

    assert result == mock_user
    assert main_controller.authenticated_user == mock_user


def test_authenticate_user_controller_fail(main_controller, monkeypatch):
    # on simule une auth qui lève une exception
    def mock_authenticate_user(email, password):
        raise AuthenticationError()

    # on remplace la methode avec monkeypatch
    monkeypatch.setattr(main_controller.user_service, "authenticate_user", mock_authenticate_user)

    with pytest.raises(AuthenticationError):
        main_controller.authenticate_user_controller("test@example.com", "wrong_password")


def test_verify_and_refresh_token(main_controller, monkeypatch, mock_user):
    def mock_load_tokens():
        return {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token'
        }

    def mock_verify_token(token):
        if token == 'test_access_token':
            return None  # on simule que le token a expiré en retournant none
        return {'user_id': 1}

    def mock_refresh_access_token(refresh_token):
        return "new_access_token"

    def mock_save_tokens(new_access_token, refresh_token):
        pass

    def mock_fetch_user_from_token(decoded_token):
        return mock_user

    # on remplace les methodes avec monkeypatch
    monkeypatch.setattr(main_controller.token_manager, "load_tokens", mock_load_tokens)
    monkeypatch.setattr(main_controller.token_manager, "verify_token", mock_verify_token)
    monkeypatch.setattr(main_controller.token_manager, "refresh_access_token", mock_refresh_access_token)
    monkeypatch.setattr(main_controller.token_manager, "save_tokens", mock_save_tokens)
    monkeypatch.setattr(main_controller, "_fetch_user_from_token", mock_fetch_user_from_token)

    result = main_controller.verify_and_refresh_token()

    assert result == mock_user


def test_controller_logout(main_controller, mocker, monkeypatch, mock_authenticated_user):
    # Utiliser un mocker pour créer un mock de delete_tokens
    mock_delete_tokens = mocker.Mock()
    # on simule un utilisateur authentifié
    main_controller.authenticated_user = mock_authenticated_user
    # on remplace delete_tokens par le mock
    monkeypatch.setattr(main_controller.token_manager, "delete_tokens", mock_delete_tokens)

    main_controller.logout()

    assert main_controller.authenticated_user is None
    mock_delete_tokens.assert_called_once()
