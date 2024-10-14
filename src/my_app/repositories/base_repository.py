"""
This file contains :
    generic interface for repositories
    the generic SQLAlchemy implementation
    the decorator for executing transactions (exec_transaction)
"""

import yaml
from datetime import datetime
import pytz
from functools import wraps

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import TypeVar, Generic, List, Optional, Type


# TODO : ne pas lire plusieurs fois les fichiers de param, a centraliser au démarrage de l'app
# récupération de la time_zone depuis le fichier config.yaml
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
TIME_ZONE_NAME = config['global']['TIME_ZONE']
TIME_ZONE = pytz.timezone(TIME_ZONE_NAME)


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
        # # ajout d'un filtre (active) présent dans le BaseModel pour gérer le soft delete
        # return self.model.active(self.db_session).filter(self.model.id == entity_id).first()
        return self.db_session.query(self.model).filter(self.model.id == entity_id,
                                                        self.model.deleted_at.is_(None)).first()

    def get_all(self) -> List[T]:
        # TODO ajouter de la pagination il peut y avoir beaucoup de données
        # TODO limiter la selection des colonnes dans les entités enfant
        # note : Si on ne veut pas avoir accès a cette methode dans la class\
        # enfant lever une exception NotImplementedError

        # # ajout d'un filtre (active) présent dans le BaseModel pour gérer le soft delete
        # return self.model.active(self.db_session).all()
        return self.db_session.query(self.model).filter(self.model.deleted_at.is_(None)).all()

    @exec_transaction
    def add(self, entity: T) -> T:
        self.db_session.add(entity)
        return entity

    @exec_transaction
    def update(self, entity: T, update_data: dict) -> T:
        # si l'entité n'existe pas on lève une exception
        if not entity:
            raise Exception(f"{self.model.__name__} not found")
        # Dans le cas ou l'entité a été soft delete, on n'autorise pas l'update
        # protection supplémentaire car normalement un get est logiquement appelé avant.
        if entity.deleted_at is not None:
            raise Exception(f"Can't update a deleted object : {self.model.__name__}")

        # mise à jour des attributs
        for key, value in update_data.items():
            setattr(entity, key, value)
        return entity

    @exec_transaction
    def delete(self, entity: T) -> None:
        """sof delete"""
        # si l'entité n'existe pas on lève une exception
        if not entity:
            raise Exception(f"{self.model.__name__} not found")
        entity.deleted_at = datetime.now(TIME_ZONE)
