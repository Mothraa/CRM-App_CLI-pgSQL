# Le repository spécifique pour la gestion des utilisateurs.
# Il hérite de l'implémentation générique SQLAlchemyRepository
from typing import Optional

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

    def get_by_email(self, email: str) -> Optional[User]:
        """get an user by his email."""
        # add a filter to exclude soft deleted entities
        # return None if not found
        return self.db_session.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()

    def is_user_exist_by_id(self, user_id: int) -> bool:
        """Checks if a user exists by ID"""
        # scalar : pour retourner qu'un element dans sqlalchemy
        # add a filter to exclude soft deleted entities
        return self.db_session.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).scalar()

    def is_user_exist_by_email(self, email: str) -> bool:
        """Checks if a user exists by email"""
        # add a filter to exclude soft deleted entities
        # scalar : pour retourner qu'un element dans sqlalchemy
        return self.db_session.query(exists().where(User.email == email, User.deleted_at.is_(None))).scalar()
