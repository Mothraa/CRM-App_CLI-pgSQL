# Le repository spécifique pour la gestion des clients.

from sqlalchemy.orm import Session
from my_app.models import Customer
from my_app.repositories.base_repository import SQLAlchemyRepository


class CustomerRepository(SQLAlchemyRepository[Customer]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Customer)
