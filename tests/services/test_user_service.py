import pytest

from sqlalchemy.exc import IntegrityError
from my_app.models import User, RoleType


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
def test_create_user(mock_session, user_service):
    """Test user account creation"""
    email = "michel@test.com"
    password = "super_password"
    first_name = "Michel"
    last_name = "LeTesteur"
    role = RoleType.admin

    user = user_service.create_user(email, password, first_name, last_name, role)

    # TODO a comparer a l'utilisateur mocké
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert user.email == email
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.role == role


@pytest.mark.unit
def test_create_user_duplicate_email(mock_session, user_service):
    """Test user account creation with already taken email"""
    # on redefini la methode add pour lever une exception d'unicité / intégrité
    def mock_add(user):
        raise IntegrityError(statement=None, params=None, orig="fake_exception_message")  # fake exception params
    mock_session.add = mock_add

    # Vérifier que l'exception IntegrityError est levée lors de la création d'un utilisateur avec un email déjà pris
    with pytest.raises(IntegrityError):
        user_service.create_user("michel@test.com", "super_password", "Michel", "LeTesteur", RoleType.admin)


@pytest.mark.unit
def test_create_test_accounts(user_service, mock_session, mocker):
    """Test for creating test user accounts (only used in dev mode)"""
    # mocker => fixture du module pytest-mock
    # Utilisation de side_effect => on simule un nouvel utilisateur a chaque appel de create_user
    user_service.create_user = mocker.Mock(side_effect=[
        User(email="test_admin@test.com", password_hash="my_password_hashed",
             first_name="Test", last_name="User_admin", role=RoleType.admin),
        User(email="test_manage@test.com", password_hash="my_password_hashed",
             first_name="Test", last_name="User_manage", role=RoleType.manage),
        User(email="test_sales@test.com", password_hash="my_password_hashed",
             first_name="Test", last_name="User_sales", role=RoleType.sales),
        User(email="test_support@test.com", password_hash="my_password_hashed",
             first_name="Test", last_name="User_support", role=RoleType.support),
    ])

    created_users = user_service.create_test_accounts()

    # On vérifie que create_user a été appelé 4 fois (une fois pour chaque role utilisateur)
    assert user_service.create_user.call_count == 4
    # on vérifie que les utilisateurs correspondent bien a ceux souhaités
    assert created_users[0].email == "test_admin@test.com"
    assert created_users[1].email == "test_manage@test.com"
    assert created_users[2].email == "test_sales@test.com"
    assert created_users[3].email == "test_support@test.com"
