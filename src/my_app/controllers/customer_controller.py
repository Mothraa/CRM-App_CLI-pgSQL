from my_app.services.customer_service import CustomerService
from my_app.controllers.base_controller import BaseController
from my_app.services.user_service import UserService
from my_app.exceptions import InvalidUserRole
from my_app.permissions import check_permission
from my_app.models import RoleType


class CustomerController(BaseController):
    def __init__(self, customer_service: CustomerService, user_service: UserService):
        """Inherits common methods from BaseController"""
        super().__init__(customer_service)
        self.user_service = user_service

    def list(self, user):
        check_permission(user, "view-customer")
        return super().list()

    def get(self, customer_id: int, user):
        """Retrieve a specific customer by ID"""
        check_permission(user, "view-customer")
        return super().get(customer_id)

    def add(self, user, customer_data: dict):
        check_permission(user, "add-customer")
        # on affecte l'utilisateur créateur en tant que contact vente par défaut
        customer_data.setdefault("contact_sales_id", user.id)

        return super().add(customer_data, user)

    def update(self, customer_id, customer_data: dict, user):
        check_permission(user, "update-customer")
        # on récupère le client, pour vérifier le commercial responsable
        customer = self.customer_service.get_by_id(customer_id)
        # il faut que l'utilisateur courant soit le commercial responsable
        if customer.contact_sales_id != user.id:
            raise PermissionError("Only the responsible sales contact can update the customer")

        # pour la mise à jour, on verifie si "contact_sales_id" est dans "customer_data"
        contact_sales_id = customer_data.get("contact_sales_id")
        if contact_sales_id:
            # on vérifie que c'est bien un utilisateur avec le role "sales"
            sales_contact = self.user_service.get_by_id(contact_sales_id)
            if sales_contact.role != RoleType.sales:
                full_name = f"{sales_contact.first_name} {sales_contact.last_name}"
                raise InvalidUserRole(sales_contact.id, full_name)

        return super().update(customer_id, customer_data, user)

    def delete(self, user, customer_id):
        check_permission(user, "delete-customer")
        return super().delete(customer_id, user)
