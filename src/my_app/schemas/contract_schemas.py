from pydantic import BaseModel, Field
from typing import Optional
from my_app.models import ContractStatus  # On réutilise l'énumération du modèle


class BaseContractSchema(BaseModel):
    """Base schema with common validators"""

    model_config = {
        # Permet de passer une session SQLAlchemy à Pydantic, utile pour la sérialisation d'objets ORM
        "from_attributes": True,
        # Permet l'utilisation des noms d'attributs du modèle en plus des alias de champ Pydantic
        "populate_by_name": True
    }


class ContractAddSchema(BaseContractSchema):
    """Schema to validate data for contract creation (add)"""
    customer_id: int = Field(...)
    contact_sales_id: int = Field(...)
    total_amount: Optional[float] = Field(None)
    remaining_amount: Optional[float] = Field(None)
    status: ContractStatus = Field(...)  # enum du model


class ContractUpdateSchema(BaseContractSchema):
    """Schema to validate data for contract modification (update)"""
    customer_id: Optional[int] = Field(None)
    contact_sales_id: Optional[int] = Field(None)
    total_amount: Optional[float] = Field(None)
    remaining_amount: Optional[float] = Field(None)
    status: Optional[ContractStatus] = Field(None)  # enum du model
