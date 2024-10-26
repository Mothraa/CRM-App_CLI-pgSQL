
class BaseController:
    def __init__(self, service):
        """
        Base controller to manage common operations for any entity.
        param:
            service => the service layer responsible for CRUD operations on the entity
        """
        self.service = service

    def list(self):
        """Retrieve all entities"""
        return self.service.get_all()

    def get(self, entity_id: int):
        """Retrieve an entity by ID"""
        return self.service.get_by_id(entity_id)

    # TODO : remove current_user, les permissions sont vérifiées dans le controleur maintenant et plus dans le service
    def add(self, entity_data: dict):
        """Create a new entity"""
        return self.service.add(entity_data)

    def update(self, entity_id: int, update_data: dict):
        """Update an entity's data"""
        return self.service.update(entity_id, update_data)

    def delete(self, entity_id: int):
        """(soft) delete an entity"""
        return self.service.delete(entity_id)
