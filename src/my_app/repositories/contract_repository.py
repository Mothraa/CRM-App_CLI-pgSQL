# Le repository spécifique pour la gestion des contrats.

from sqlalchemy.orm import Session
from my_app.models import Contract
from my_app.repositories.base_repository import SQLAlchemyRepository


class ContractRepository(SQLAlchemyRepository[Contract]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Contract)

    def filter_by_status(self, statuts: list):
        """Return contracts with the specified status"""
        return self.db_session.query(Contract).filter(Contract.status.in_(statuts)).all()

    def filter_by_notpaid_contracts(self):
        """Return contracts who are not full paid"""
        return self.db_session.query(Contract).filter(Contract.remaining_amount != 0).all()
