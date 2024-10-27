from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BaseEventSchema(BaseModel):
    """Base schema with common validators"""

    model_config = {
        # Permet de passer une session SQLAlchemy à Pydantic, utile pour la sérialisation d'objets ORM
        "from_attributes": True,
        # Permet l'utilisation des noms d'attributs du modèle en plus des alias de champ Pydantic
        "populate_by_name": True
    }


class EventAddSchema(BaseEventSchema):
    """Schema to validate data for event creation (add)"""
    name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    attendees: Optional[str] = Field(None, max_length=255, description="Nom des participants")
    comments: Optional[str] = Field(None, max_length=255)
    contract_id: int = Field(...)


class EventUpdateSchema(BaseEventSchema):
    """Schema to validate data for event modification (update)"""
    name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    attendees: Optional[str] = Field(None, max_length=255, description="Nom des participants")
    comments: Optional[str] = Field(None, max_length=255)
    contract_id: Optional[int] = Field(None)
    contact_support_id: Optional[int] = Field(None)
