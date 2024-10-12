# Le repository spécifique pour la gestion des utilisateurs.
# Il hérite de l'implémentation générique SQLAlchemyRepository

from sqlalchemy import exists
from sqlalchemy.orm import Session
from my_app.models import User
from my_app.repositories.base_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    """
    note : get_by_id, get_all, add, update et delete hérités de SQLAlchemyRepository
    """
    def __init__(self, db_session: Session):
        super().__init__(db_session, User)

    def get_by_email(self, email: str) -> User:
        """get an user by his email."""
        return self.db_session.query(User).filter_by(email=email).first()

    def is_user_exist_by_id(self, user_id: int) -> bool:
        """Checks if a user exists by ID"""
        # scalar : pour retourner qu'un element dans sqlalchemy
        return self.db_session.query(User).exists().where(User.id == user_id).scalar()

    def is_user_exist_by_email(self, email: str) -> bool:
        """Checks if a user exists by email"""
        # scalar : pour retourner qu'un element dans sqlalchemy
        return self.db_session.query(exists().where(User.email == email)).scalar()

    # @exec_transaction
    # def create_user(self, user_data: dict) -> User:
    #     """Create a new user in db"""
    #     new_user = User(**user_data)
    #     self.db_session.add(new_user)
    #     return new_user

    # @exec_transaction
    # def update_user(self, user_id: int, update_data: dict) -> User:
    #     """Updates a user with updated data"""
    #     user = self.get_by_id(user_id)
    #     if not user:
    #         raise Exception("User not found")
    #     for key, value in update_data.items():
    #         setattr(user, key, value)
    #     return user

    # @exec_transaction
    # def delete_user(self, user_id: int) -> bool:
    #     """Deletes a user by their ID"""
    #     user = self.get_by_id(user_id)
    #     if not user:
    #         raise Exception("User not found")
    #     self.db_session.delete(user)
