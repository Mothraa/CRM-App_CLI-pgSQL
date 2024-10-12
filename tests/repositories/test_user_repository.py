import pytest
from my_app.models import User
from my_app.repositories.user_repository import UserRepository


def test_get_user_by_id_success(mock_session, mock_user):
    """Test to retrieve a user by a correct ID"""
    repository = UserRepository(mock_session)

    # création d'un mock pour query et get
    query = mock_session.query.return_value
    query.get.return_value = mock_user  # get présent dans get_by_id

    result = repository.get_by_id(mock_user.id)

    assert result == mock_user
    mock_session.query(User).get.assert_called_once_with(mock_user.id)


def test_get_user_by_id_not_found(mock_session):
    """Test to retrieve a user by a (false - not found) ID"""
    # mock_session.query(User).filter_by(id=666).first.return_value = None
    repository = UserRepository(mock_session)

    # création d'un mock pour query et get
    query = mock_session.query.return_value
    query.get.return_value = None  # simulation d'un user non trouvé

    result = repository.get_by_id(666)  # try to call satan 😈

    assert result is None
    mock_session.query(User).get.assert_called_once_with(666)


def test_get_user_by_email_success(mock_session, mock_user):
    """Test to retrieve a user by a correct email"""
    fake_valid_email = "michel@test.com"
    repository = UserRepository(mock_session)

    # création d'un mock pour query et get
    query = mock_session.query.return_value
    query.filter_by.return_value = query
    query.first.return_value = mock_user

    result = repository.get_by_email(fake_valid_email)

    assert result == mock_user
    mock_session.query(User).filter_by.assert_called_once_with(email=fake_valid_email)


# décorateur qui permet le test de plusieurs cas
@pytest.mark.parametrize("user_id, user_exists", [(8, True), (666, False),])
def test_is_user_exist_by_id(mock_session, user_id, user_exists):
    """Test checking function "is_user_exist_by_id"""
    # création des mocks
    mock_query = mock_session.query.return_value
    mock_exists = mock_query.exists.return_value
    mock_where = mock_exists.where.return_value
    mock_where.scalar.return_value = user_exists

    repository = UserRepository(mock_session)

    result = repository.is_user_exist_by_id(user_id)

    assert result == user_exists
    # mock_exists.where.assert_called_once_with(User.id == user_id)
    # mock_exists.where.assert_called_once_with(ANY)
    assert mock_exists.where.called
    mock_where.scalar.assert_called_once()


# # CONSERVE SI BESOIN POUR D'AUTRES TABLES, mais inutile de tester ici car passé dans le repository générique (base)
# def test_add_user_success(mock_session, mock_user):
#     """Test add a user => OK"""
#     # creation d'une instance de User à partir des données du mock
#     new_user = User(
#         email=mock_user.email,
#         first_name=mock_user.first_name,
#         last_name=mock_user.last_name,
#         password_hash=mock_user.password_hashed,
#         role=mock_user.role
#     )

#     repository = UserRepository(mock_session)

#     new_user_added = repository.add(new_user)

#     assert isinstance(new_user_added, User)
#     mock_session.add.assert_called_once_with(new_user_added)
#     mock_session.commit.assert_called_once()


# # CONSERVE SI BESOIN POUR D'AUTRES TABLES, mais inutile de tester ici car passé dans le repository générique (base)
# def test_create_user_fail(mock_session, mock_user):
#     """Test when user creation fail => transaction rollback called"""
#     # creation d'une instance de User à partir des données du mock
#     new_user = User(
#         email=mock_user.email,
#         first_name=mock_user.first_name,
#         last_name=mock_user.last_name,
#         password_hash=mock_user.password_hashed,
#         role=mock_user.role
#     )
#     repository = UserRepository(mock_session)

#     # simulation d'une erreur sqlalchemy
#     mock_session.add.side_effect = SQLAlchemyError("Simulated Error !")

#     # on verifie que l'exception est bien levée et que le rollback est bien appelé
#     with pytest.raises(Exception) as excinfo:
#         repository.add(new_user)

#     assert "Transaction failed" in str(excinfo.value)
#     mock_session.rollback.assert_called_once()


# # CONSERVE SI BESOIN POUR D'AUTRES TABLES, mais inutile de tester ici car passé dans le repository générique (base)
# def test_update_user_success(mock_session, mock_user):
#     """Test update a user => OK"""
#     mock_user_data = {"last_name": "Nouveau_nom"}
#     repository = UserRepository(mock_session)

#     updated_user = repository.update(mock_user, mock_user_data)

#     assert updated_user.last_name == "Nouveau_nom"
#     mock_session.commit.assert_called_once()


# # CONSERVE SI BESOIN POUR D'AUTRES TABLES, mais inutile de tester ici car passé dans le repository générique (base)
# def test_update_user_fail(mock_session):
#     """Test update a user fail (that doesn't exist)"""
#     mock_user_data = {"last_name": "Nouveau_nom"}
#     mock_session.query(User).get.return_value = None

#     repository = UserRepository(mock_session)

#     # utilisateur inexistant
#     missing_user = None

#     # Vérifie que l'exception "User not found" est levée
#     with pytest.raises(Exception) as excinfo:
#         repository.update(missing_user, mock_user_data)

#     assert "User not found" in str(excinfo.value)
#     mock_session.commit.assert_not_called()


# # CONSERVE SI BESOIN POUR D'AUTRES TABLES, mais inutile de tester ici car passé dans le repository générique (base)
# def test_delete_user_success(mock_session, mock_user):
#     """Test delete a user with success"""
#     mock_session.query(User).filter_by(id=mock_user.id).first.return_value = mock_user
#     repository = UserRepository(mock_session)

#     result = repository.delete(mock_user)

#     mock_session.delete.assert_called_once_with(mock_user)
#     mock_session.commit.assert_called_once()


# # CONSERVE SI BESOIN POUR D'AUTRES TABLES, mais inutile de tester ici car passé dans le repository générique (base)
# def test_delete_user_fail(mock_session):
#     """Test deleting a user fail (that doesn't exist)"""
#     mock_session.query(User).get.return_value = None
#     repository = UserRepository(mock_session)

#     with pytest.raises(Exception) as excinfo:
#         user_to_delete = repository.get_by_id(666)
#         repository.delete(user_to_delete)

#     assert "User not found" in str(excinfo.value)
#     mock_session.commit.assert_not_called()
