# Le repository spécifique pour la gestion des contrats.

from sqlalchemy.orm import Session
from my_app.models import Contract
from my_app.repositories.base_repository import SQLAlchemyRepository


class ContractRepository(SQLAlchemyRepository[Contract]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Contract)
