import pytest
from unittest.mock import MagicMock

from my_app.models import RoleType
from my_app.services.user_service import UserService


# fixture specifique a UserService
@pytest.fixture
def user_service(mock_session, monkeypatch):
    """Fixture for creating an UserService instance with a mocked session and repository"""
    mock_user_repository = MagicMock()

    # on instancie le service
    user_service = UserService(user_repository=mock_user_repository, session=mock_session)

    return user_service


@pytest.mark.unit
def test_hash_password(user_service):
    """Test password hashing function"""
    password = "my_password"
    hashed_password = user_service.hash_password(password)

    assert hashed_password != password
    assert user_service.verify_password(hashed_password, password)


@pytest.mark.unit
def test_salted_password(user_service):
    """Test if an hashed password is salted too"""
    password = "my_password"
    # on génère deux hash du même mot de passe
    hashed_password1 = user_service.hash_password(password)
    hashed_password2 = user_service.hash_password(password)

    # on verifie que les hash sont bien différents
    assert hashed_password1 != hashed_password2


@pytest.mark.unit
def test_verify_password(user_service):
    """Test the function who verify the password"""
    password = "my_password"
    hashed_password = user_service.hash_password(password)

    assert user_service.verify_password(hashed_password, password)
    assert not user_service.verify_password(hashed_password, "wrong_password")


@pytest.mark.unit
def test_add_user(mock_session, user_service, mock_user):
    """Test user account creation"""
    user_data = {
        "email": "patrick@test.com",
        "password": "Super_passwordQuiR3spectLéContraintes!!",
        "first_name": "Patrick",
        "last_name": "LeVendeur",
        "role": RoleType.admin,
    }
    # on simule que le mail n'est pas déjà utilisé
    user_service.user_repository.get_by_email.return_value = None

    # ajout d'un utilisateur
    user_service.add(user_data=user_data)

    user_service.user_repository.add.assert_called_once()

    # TODO : test a completer
    # # Vérification des attributs du nouvel utilisateur créé
    # assert new_user.email == user_data["email"]
    # assert new_user.first_name == user_data["first_name"]
    # assert new_user.last_name == user_data["last_name"]
    # assert new_user.role == user_data["role"]
    # # on verifie que le mdp a été stocké en hashé
    # assert new_user.password_hash != user_data["password"]


@pytest.mark.unit
def test_create_user_duplicate_email(mock_session, user_service, mock_user):
    """Test user account creation with already taken email"""
    # on simule que l'email existe déjà dans la db
    user_service.user_repository.get_by_email.return_value = mock_user

    user_data = {
        "email": "michel@test.com",
        "password": "Super_passwordQuiR3spectLéContraintes",
        "first_name": "Michel",
        "last_name": "LeTesteur",
        "role": RoleType.admin,
    }

    # on vérifie la levée d'exception lors de la création d'un utilisateur avec un email déjà pris
    with pytest.raises(ValueError, match="Email is already used"):
        user_service.add(user_data=user_data)

# @pytest.mark.unit
# def test_create_test_accounts(user_service, mock_session, mocker):
#     """Test for creating test user accounts (only used in dev mode)"""
#     # mocker => fixture du module pytest-mock
#     # Utilisation de side_effect => on simule un nouvel utilisateur a chaque appel de create_user
#     user_service.create_user = mocker.Mock(side_effect=[
#         User(email="test_admin@test.com", password_hash="my_password_hashed",
#              first_name="Test", last_name="User_admin", role=RoleType.admin),
#         User(email="test_manage@test.com", password_hash="my_password_hashed",
#              first_name="Test", last_name="User_manage", role=RoleType.manage),
#         User(email="test_sales@test.com", password_hash="my_password_hashed",
#              first_name="Test", last_name="User_sales", role=RoleType.sales),
#         User(email="test_support@test.com", password_hash="my_password_hashed",
#              first_name="Test", last_name="User_support", role=RoleType.support),
#     ])

#     created_users = user_service.create_test_accounts()

#     # On vérifie que create_user a été appelé 4 fois (une fois pour chaque role utilisateur)
#     assert user_service.create_user.call_count == 4
#     # on vérifie que les utilisateurs correspondent bien a ceux souhaités
#     assert created_users[0].email == "test_admin@test.com"
#     assert created_users[1].email == "test_manage@test.com"
#     assert created_users[2].email == "test_sales@test.com"
#     assert created_users[3].email == "test_support@test.com"
