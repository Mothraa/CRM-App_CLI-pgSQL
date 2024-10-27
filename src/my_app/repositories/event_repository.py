# Le repository spécifique pour la gestion des événements.

from sqlalchemy.orm import Session
from my_app.models import Event
from my_app.repositories.base_repository import SQLAlchemyRepository


class EventRepository(SQLAlchemyRepository[Event]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Event)

    def filter_by_contact_support_id(self, contact_support_id):
        """Filter contact by contact_support_id"""
        return self.db_session.query(Event).filter(Event.contact_support_id == contact_support_id).all()
