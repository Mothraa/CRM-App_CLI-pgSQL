from my_app.controllers.base_controller import BaseController
from my_app.exceptions import InvalidUserRole
from my_app.permissions import check_permission
from my_app.models import RoleType


class EventController(BaseController):
    def __init__(self, event_service, contract_service, user_service):
        """Inherits common methods from BaseController"""
        super().__init__(event_service)
        self.contract_service = contract_service
        self.user_service = user_service

    def list(self, user, filter_no_support=False, assigned=False):
        check_permission(user, "view-event")
        if filter_no_support:
            return self.service.get_events_without_support()
        if assigned:
            return self.service.get_events_assigned_to_current_support_user(user.id)
        return super().list()

    def get(self, user, event_id):
        """Retrieve a specific event by ID"""
        check_permission(user, "view-event")
        return super().get(event_id)

    def add(self, user, event_data: dict):
        check_permission(user, "add-event")
        # on vérifie que le contrat est au statut 'signed'
        contract_id = event_data.get("contract_id")
        contract = self.contract_service.get_by_id(contract_id)
        if contract.status != "signed":
            raise ValueError("Un évènement ne peut être ajouté qu'à un contrat au statut signé ('signed').")
        return super().add(event_data)

    def update(self, user, event_id, event_data: dict):
        check_permission(user, "update-event")
        # on verifie si "contact_support_id" est présent dans "event_data"
        contact_support_id = event_data.get("contact_support_id")
        if contact_support_id:
            # on récupère l'utilisateur et verif son role
            support_contact = self.user_service.get_by_id(contact_support_id)
            if support_contact.role != RoleType.support:
                full_name = f"{support_contact.first_name} {support_contact.last_name}"
                raise InvalidUserRole(support_contact.id, full_name)

        return super().update(event_id, event_data)

    def delete(self, user, event_id):
        check_permission(user, "delete-event")
        return super().delete(event_id)
