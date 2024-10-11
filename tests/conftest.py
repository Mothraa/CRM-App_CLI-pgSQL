import pytest
import datetime

from my_app.services.user_service import UserService  # Assure-toi d'importer UserService correctement


@pytest.fixture
def mock_session(mocker):
    """Fixture for simulate a session SQLAlchemy and his methods"""
    session = mocker.Mock()
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
                return mock_time.astimezone(tz)  # utilise la timezone si indiqué
            return mock_time

    monkeypatch.setattr(datetime, "datetime", MockDateTime)
    return fake_time


@pytest.fixture
def mock_user(monkeypatch):
    """Fixture to mock a user"""
    class MockUser:
        def __init__(self, user_id):
            self.id = user_id

    # TODO : a revoir une fois les couches d'abstraction ajoutées (uniquement l'id pour l'instant)
    return MockUser(user_id=8)
