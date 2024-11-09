import datetime
import os
import pytest
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from my_app.models import RoleType
from my_app.db_config import get_engine

# on charge la variable d'environnement
load_dotenv(override=True)
DATABASE_TEST_NAME = os.getenv("DATABASE_TEST_NAME")


@pytest.fixture
def mock_session(mocker):
    """Fixture for simulate a session SQLAlchemy and his methods"""
    session = mocker.Mock()

    # "mockage" des transactions
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


@dataclass
class MockUser:
    id: int = 8
    email: str = "michel@test.com"
    password_hashed: str = "hashed_password"
    first_name: str = "Michel"
    last_name: str = "LeTesteur"
    role: RoleType = RoleType.admin
    created_at: Optional[datetime.datetime] = field(default=None)
    updated_at: Optional[datetime.datetime] = field(default=None)
    deleted_at: Optional[datetime.datetime] = field(default=None)


@pytest.fixture
def mock_user():
    """Fixture to mock a user"""
    return MockUser()


class MockAuthenticatedUser:
    def __init__(self, user_id=8, email="michel@test.com", role=RoleType.admin):
        self.id = user_id
        self.email = email
        self.role = role


# utilisateur authentifié (de plus haut niveau), principalement pour le test des controleurs/vues
@pytest.fixture
def mock_authenticated_user(mock_user):
    """Fixture for an authenticated user"""
    return MockAuthenticatedUser(user_id=mock_user.id, email=mock_user.email, role=mock_user.role)


@pytest.fixture(scope="session")  # session : créé une seule fois pour l'ensemble des tests
def db_engine():
    """Create an engine for the test database"""
    # Créer l'engine pour la base de test
    engine = get_engine(database_name=DATABASE_TEST_NAME)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Creates a new database session for each test"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()
