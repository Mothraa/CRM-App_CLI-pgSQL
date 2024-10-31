from my_app.decorators import log_user_actions
from my_app.models import Event
from my_app.schemas.event_schemas import EventAddSchema, EventUpdateSchema
from my_app.exceptions import EventNotFoundError


class EventService:
    def __init__(self, session, event_repository):
        """
        Services to create and manage event data.
        param :
            session => the SQLAlchemy session to manage the database
            event_repository => repository to manage event data/sqlalchemy operations
        """
        self.session = session
        self.event_repository = event_repository

    def get_by_id(self, event_id: int):
        """Retrieve an event by its ID"""
        event = self.event_repository.get_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"No event with ID: {event_id}")
        return event

    def get_all(self):
        """Retrieve all events"""
        return self.event_repository.get_all()

    def get_events_without_support(self):
        """Return events not assigned (to support contact user)"""
        return self.event_repository.filter_by_contact_support_id(None)

    def get_events_assigned_to_current_support_user(self, user_id: int):
        """Return events assigned to a specific user (support)"""
        return self.event_repository.filter_by_contact_support_id(user_id)

    @log_user_actions("Ajout d'un évènement")
    def add(self, event_data: dict) -> Event:
        """Method to add a new event"""
        # on valide les données d'entrée avec pydantic
        event_add = EventAddSchema(**event_data)
        # on converti les données pydantic en dict
        event_add_dict = event_add.model_dump()
        # on créé le nouvel Event via le repository
        # TODO : passer un dict pour éviter une dépendance au modèle
        new_event = self.event_repository.add(Event(**event_add_dict))
        return new_event

    @log_user_actions("Mise à jour d'un évènement")
    def update(self, event_id: int, update_data: dict):
        """Method to update an existing event."""
        # on valide les données d'entrée avec pydantic
        event_update = EventUpdateSchema(**update_data)

        # on récupère les données a mettre à jour
        event_to_update = self.event_repository.get_by_id(event_id)
        if not event_to_update:
            raise EventNotFoundError(f"No event with ID: {event_id}")

        data_to_update_dict = event_update.model_dump(exclude_unset=True)
        # # on applique la mise à jour des attributs
        for key, value in data_to_update_dict.items():
            setattr(event_to_update, key, value)
        # sauvegarde via le repository
        updated_event = self.event_repository.update(event_to_update,  data_to_update_dict)
        return updated_event

    @log_user_actions("Suppression d'un évènement")
    def delete(self, event_id: int):
        """Method to delete an event (soft delete)."""
        # on récupère l'Event à supprimer
        event_to_delete = self.event_repository.get_by_id(event_id)
        if not event_to_delete:
            raise EventNotFoundError(f"No event with ID: {event_id}")

        # on fait le (soft) delete via le repository
        self.event_repository.delete(event_to_delete)
        # on ne retourne rien, par cohérence avec le repository et pour ne pas exposer les données
