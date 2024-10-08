import pytest

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
