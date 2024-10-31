from my_app.decorators import log_user_actions
from my_app.models import Contract
from my_app.schemas.contract_schemas import ContractAddSchema, ContractUpdateSchema
from my_app.exceptions import ContractNotFoundError


class ContractService:
    def __init__(self, session, contract_repository):
        """
        Services to create and manage contract data.
        param :
            session => the SQLAlchemy session to manage the database
            contract_repository => repository to manage contract data/sqlalchemy operations
        """
        self.session = session
        self.contract_repository = contract_repository

    def get_by_id(self, contract_id: int):
        """Retrieve a contract by its ID"""
        contract = self.contract_repository.get_by_id(contract_id)
        if not contract:
            raise ContractNotFoundError(f"No contract with ID: {contract_id}")
        return contract

    def get_all(self):
        """Retrieve all contracts"""
        return self.contract_repository.get_all()

    def get_unsigned_contracts(self):
        """Return contracts that ar not already signed (exclude cancelled and finished) => to_send and pending"""
        return self.contract_repository.filter_by_status(["to_send", "pending"])

    def get_notpaid_contracts(self):
        return self.contract_repository.filter_by_notpaid_contracts()

    @log_user_actions("Creation d'un contrat")
    def add(self, contract_data: dict):
        """Method to add a new contract"""
        # on valide les données d'entrée avec pydantic
        contract_add = ContractAddSchema(**contract_data)
        # on convertit les données pydantic en dict
        contract_add_dict = contract_add.model_dump()
        # on créé le nouveau Contract via le repository
        # TODO : passer un dict pour éviter une dépendance au modèle
        new_contract = self.contract_repository.add(Contract(**contract_add_dict))
        return new_contract

    @log_user_actions("Mise à jour d'un contrat")
    def update(self, contract_id: int, update_data: dict):
        """Method to update an existing contract."""
        # on valide les données d'entrée avec pydantic
        contract_update = ContractUpdateSchema(**update_data)

        # on récupère les données à mettre à jour
        contract_to_update = self.contract_repository.get_by_id(contract_id)
        if not contract_to_update:
            raise ContractNotFoundError(f"No contract with ID: {contract_id}")

        # on applique la mise à jour des attributs
        data_to_update_dict = contract_update.model_dump(exclude_unset=True)
        for key, value in data_to_update_dict.items():
            setattr(contract_to_update, key, value)
        # sauvegarde via le repository
        updated_contract = self.contract_repository.update(contract_to_update, data_to_update_dict)
        return updated_contract

    @log_user_actions("Suppression d'un contrat")
    def delete(self, contract_id: int):
        """Method to delete a contract (soft delete)."""
        # on récupère le Contract à supprimer
        contract_to_delete = self.contract_repository.get_by_id(contract_id)
        if not contract_to_delete:
            raise ContractNotFoundError(f"No contract with ID: {contract_id}")

        # on fait le (soft) delete via le repository
        self.contract_repository.delete(contract_to_delete)
        # on ne retourne rien, par cohérence avec le repository et pour ne pas exposer les données
