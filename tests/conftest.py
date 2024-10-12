import pytest
import datetime

from my_app.services.user_service import UserService  # Assure-toi d'importer UserService correctement
from my_app.models import RoleType


@pytest.fixture
def mock_session(mocker):
    """Fixture for simulate a session SQLAlchemy and his methods"""
    session = mocker.Mock()

    # gestion des transactions
    session.add = mocker.Mock()
    session.commit = mocker.Mock()
    session.rollback = mocker.Mock()
    return session


@pytest.fixture
def user_service(mock_session):
    """Fixture for creating an UserService instance with a mocked session"""
    return UserService(session=mock_session)


@pytest.fixture
def mock_time(monkeypatch):
    """Fixture to freeze time !"""
    fake_time = datetime.datetime(2023, 1, 2, 20, 0, 0)

    class MockDateTime:
        @classmethod
        def now(cls, tz=None):
            if tz:
                return fake_time.astimezone(tz)  # utilise la timezone si indiqué
            return fake_time

    monkeypatch.setattr(datetime, "datetime", MockDateTime)
    return fake_time


@pytest.fixture
def mock_user(monkeypatch):
    """Fixture to mock a user"""
    class MockUser:
        def __init__(self, user_id, email="michel@test.com", password="hashed_password",
                     first_name="Michel", last_name="LeTesteur", role=RoleType.admin):
            self.id = user_id
            self.email = email
            self.password_hashed = password
            self.first_name = first_name
            self.last_name = last_name
            self.role = role
    return MockUser(user_id=8)
