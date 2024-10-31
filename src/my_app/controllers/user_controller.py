from my_app.services.user_service import UserService
from my_app.controllers.base_controller import BaseController
from my_app.permissions import check_permission


class UserController(BaseController):
    def __init__(self, user_service: UserService):
        """Inherits common methods from BaseController"""
        super().__init__(user_service)

    def list(self, user):
        check_permission(user, "view-user")
        return super().list()

    def get(self, user, user_id: int):
        """Retrieve a specific user by ID"""
        check_permission(user, "view-user")
        return super().get(user_id)

    def add(self, user, user_data: dict):
        check_permission(user, "add-user")
        # on hash le password
        if "password" in user_data:
            user_data["password"] = self.user_service.hash_password(user_data["password"])
        return super().add(user_data)

    def update(self, user, user_id, user_data: dict):
        check_permission(user, "update-user")
        # on hash le password si présent dans les données a mettre à jour
        if "password" in user_data:
            user_data["password"] = self.user_service.hash_password(user_data["password"])
        return super().update(user_id, user_data)

    def delete(self, user, user_id):
        check_permission(user, "delete-user")
        return super().delete(user_id)
