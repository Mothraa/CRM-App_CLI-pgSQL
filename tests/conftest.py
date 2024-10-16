import pytest
import datetime

from sqlalchemy import Column, Integer, String, DateTime

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

        id = Column(Integer)
        deleted_at = Column(DateTime)
        # email = None
        # password_hashed = None
        # first_name = None
        # last_name = None
        # role = None
        # created_at = None
        # updated_at = None

        def __init__(self, user_id, email="michel@test.com", password="hashed_password",
                     first_name="Michel", last_name="LeTesteur", role=RoleType.admin):
            self.id = user_id
            self.email = email
            self.password_hashed = password
            self.first_name = first_name
            self.last_name = last_name
            self.role = role
            self.created_at = None
            self.updated_at = None
            self.deleted_at = None
    return MockUser(user_id=8)  # on retourne une instance
