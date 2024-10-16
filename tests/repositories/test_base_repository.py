import pytest
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from my_app.repositories.base_repository import SQLAlchemyRepository

# inclus les tests sur des erreurs de transaction (via le décorateur exec_transaction)


def test_add_transaction_success(mock_session, mock_user):
    """Test transaction success when add an entity"""
    repository = SQLAlchemyRepository(mock_session, mock_user.__class__)
    result = repository.add(mock_user)

    assert result == mock_user
    mock_session.add.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()


def test_add_transaction_fail(mock_session, mock_user):
    """Test transaction rollback fail when add an entity"""
    repository = SQLAlchemyRepository(mock_session, mock_user.__class__)

    # simulation d'une exception sqlalchemy
    def sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Fake error !")

    mock_session.add = sqlalchemy_error

    with pytest.raises(Exception) as excinfo:
        repository.add(mock_user)

    assert "Transaction failed" in str(excinfo.value)
    mock_session.rollback.assert_called_once()


def test_update_transaction_success(mock_session, mock_user):
    """Test transaction success when update an entity"""
    repository = SQLAlchemyRepository(mock_session, mock_user.__class__)
    update_data = {"last_name": "Nouveau_nom"}
    result = repository.update(mock_user, update_data)

    assert result.last_name == "Nouveau_nom"
    mock_session.commit.assert_called_once()


def test_update_transaction_fail(mock_session, mock_user):
    """Test transaction rollback fail when update an entity."""
    repository = SQLAlchemyRepository(mock_session, mock_user.__class__)

    # simulation d'une exception sqlalchemy
    def sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Fake error !")

    mock_session.commit = sqlalchemy_error

    update_data = {"last_name": "Nouveau_nom"}

    with pytest.raises(Exception) as excinfo:
        repository.update(mock_user, update_data)

    assert "Transaction failed" in str(excinfo.value)
    mock_session.rollback.assert_called_once()


def test_soft_delete_transaction_success(mock_session, mock_user):
    """Test transaction success when delete an entity"""
    repository = SQLAlchemyRepository(mock_session, mock_user.__class__)

    # appel de la methode soft delete (on vérifie qu'il ne retourne rien avec l'assert plus bas)
    result = repository.delete(mock_user)

    # on verifie que deleted_at a été mis à jour
    assert mock_user.deleted_at is not None
    assert isinstance(mock_user.deleted_at, datetime)

    # Vérification que commit() est bien appelé
    mock_session.commit.assert_called_once()

    assert result is None  # par convention, delete ne doit rien retourner


def test_soft_delete_transaction_fail(mock_session, mock_user):
    """Test transaction rollback fail when delete an entity"""
    mock_session.delete.side_effect = SQLAlchemyError("Fake error !")
    repository = SQLAlchemyRepository(mock_session, mock_user.__class__)

    # on simule une exception
    def sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Fake error !")
    mock_session.commit = sqlalchemy_error
    # on verifie que l'exception est bien levée
    with pytest.raises(Exception) as excinfo:
        repository.delete(mock_user)

    assert "Transaction failed" in str(excinfo.value)
    mock_session.rollback.assert_called_once()


def test_get_by_id(mock_session, mock_user):
    """Test to get an entity by his id"""
    # mock_session.query.return_value.get.return_value = mock_user
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    repository = SQLAlchemyRepository(mock_session, mock_user.__class__)

    result = repository.get_by_id(mock_user.id)

    assert result == mock_user
    # On vérifie que querya été appelé avec MockUser
    mock_session.query.assert_called_once_with(mock_user.__class__)
    # On vérifie que filter a été appelé une fois
    mock_session.query.return_value.filter.assert_called_once()


def test_get_all(mock_session, mock_user):
    """Test to get all entities"""
    # mock_session.query.return_value.all.return_value = [mock_user]
    mock_session.query.return_value.filter.return_value.all.return_value = [mock_user]

    repository = SQLAlchemyRepository(mock_session, mock_user.__class__)

    result = repository.get_all()

    assert result == [mock_user]
    # On vérifie que querya été appelé avec MockUser
    mock_session.query.assert_called_once_with(mock_user.__class__)
    # On vérifie que filter a été appelé une fois
    mock_session.query.return_value.filter.assert_called_once()
    # On vérifie que all a été appelé après filter
    mock_session.query.return_value.filter.return_value.all.assert_called_once()
