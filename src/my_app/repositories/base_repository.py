"""
This file contains :
    generic interface for repositories
    the generic SQLAlchemy implementation
    the decorator for executing transactions (exec_transaction)
"""

from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import TypeVar, Generic, List, Optional, Type


T = TypeVar('T')


# TODO : décorateur a déplacer dans autre fichier si jamais cela devenait a se complexifier
def exec_transaction(func):
    """Decorator to handle database transactions"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
            self.db_session.commit()
            return result
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Transaction failed: {e}")
        # pour les exceptions non liées aux transactions (pour qu'elles ne soient pas masquées)
        except Exception:
            # on fait quand même un rollback
            self.db_session.rollback()
            raise  # relance l'exception d'origine (par exemple "ID not found")
    return wrapper


# Interface générique pour les repositories
class IRepository(Generic[T]):
    def get_by_id(self, entity_id: int) -> Optional[T]:
        raise NotImplementedError

    def get_all(self) -> List[T]:
        raise NotImplementedError

    def add(self, entity: T) -> T:
        raise NotImplementedError

    def update(self, entity: T, update_data: dict) -> T:
        raise NotImplementedError

    def delete(self, entity: T) -> None:
        raise NotImplementedError


# Implémentation générique du repository avec SQLAlchemy
# TODO mise à jour de IRepository en fonction de version finale de SQLAlchemyRepository ?
class SQLAlchemyRepository(Generic[T], IRepository[T]):
    def __init__(self, db_session: Session, model: Type[T]):
        self.db_session = db_session
        self.model = model

    def get_by_id(self, entity_id: int) -> Optional[T]:
        return self.db_session.query(self.model).get(entity_id)

    def get_all(self) -> List[T]:
        # TODO ajouter de la pagination il peut y avoir beaucoup de données
        # TODO limiter la selection des colonnes dans les entités enfant
        # note : Si on ne veut pas avoir accès a cette methode dans la class\
        # enfant lever une exception NotImplementedError
        return self.db_session.query(self.model).all()

    @exec_transaction
    def add(self, entity: T) -> T:
        self.db_session.add(entity)
        return entity

    @exec_transaction
    def update(self, entity: T, update_data: dict) -> T:
        # si l'entité n'existe pas on lève une exception
        if not entity:
            raise Exception(f"{self.model.__name__} not found")
        # mise à jour des attributs
        for key, value in update_data.items():
            setattr(entity, key, value)
        return entity

    @exec_transaction
    def delete(self, entity: T) -> None:
        # si l'entité n'existe pas on lève une exception
        if not entity:
            raise Exception(f"{self.model.__name__} not found")
        self.db_session.delete(entity)
