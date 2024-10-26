from my_app.services.user_service import UserService
from my_app.controllers.base_controller import BaseController
from my_app.permissions import check_permission


class UserController(BaseController):
    def __init__(self, user_service: UserService):
        """Inherits common methods from BaseController"""
        super().__init__(user_service)

    def list(self, user):
        check_permission(user, 'view-user')
        return super().list()

    def get(self, user, user_id: int):
        """Retrieve a specific user by ID"""
        check_permission(user, 'view-user')
        return super().get(user_id)

    def add(self, user, user_data: dict):
        check_permission(user, 'add-user')
        # TODO : hash pwd
        return super().create(user_data, user)

    def update(self, user, user_id, user_data: dict):
        check_permission(user, 'update-user')
        return super().update(user_id, user_data, user)

    def delete(self, user, user_id):
        check_permission(user, 'delete-user')
        return super().delete(user_id, user)
