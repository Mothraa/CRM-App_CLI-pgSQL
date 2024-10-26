from my_app.services.contract_service import ContractService
from my_app.controllers.base_controller import BaseController
from my_app.permissions import check_permission
from my_app.models import ContractStatus


class ContractController(BaseController):
    def __init__(self, contract_service: ContractService):
        """Inherits common methods from BaseController"""
        super().__init__(contract_service)

    def list(self, user):
        check_permission(user, "view-contract")
        return super().list()

    def get(self, user, contract_id):
        """Retrieve a specific contract by ID"""
        check_permission(user, "view-contract")
        return super().get(contract_id)

    def add(self, user, contract_data: dict):
        check_permission(user, "add-contract")
        # statut par défaut à "to_send" si pas spécifié
        if contract_data.get("status") is None:
            contract_data["status"] = ContractStatus.to_send.value
        # contract_data.setdefault("status", ContractStatus.to_send.value)
        return super().add(contract_data)

    def update(self, user, contract_id, contract_data: dict):
        check_permission(user, "update-contract")
        return super().update(contract_id, contract_data)

    # pas de delete possible, tous les contrats restent visibles (statut annulé possible)
    # def delete(self, user, contract_id):
    #     check_permission(user, "delete-contract")
    #     return super().delete(contract_id, user)
