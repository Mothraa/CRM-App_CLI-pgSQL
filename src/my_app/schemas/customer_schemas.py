from typing import Optional
from typing_extensions import Annotated

from pydantic import BaseModel, Field, StringConstraints


class BaseCustomerSchema(BaseModel):
    """Base schema with common validators"""

    model_config = {
        # Permet de passer une session SQLAlchemy à Pydantic, utile pour la sérialisation d'objets ORM
        "from_attributes": True,
        # Permet l'utilisation des noms d'attributs du modèle en plus des alias de champ Pydantic
        "populate_by_name": True
    }


class CustomerAddSchema(BaseCustomerSchema):
    """Schema to validate data for customer creation (add)"""
    company_name: str = Field(max_length=255, description="Company name")
    full_name: str = Field(max_length=255, description="Full name of the customer")
    phone_number: Optional[Annotated[str,
                                     StringConstraints(min_length=10, max_length=15)]
                           ] = Field(None, description="Phone number")
    contact_sales_id: int = Field(...,
                                  description="ID of the sales contact responsible for this customer"
                                  )  # ... => obligatoire (syntaxe pydantic)


class CustomerUpdateSchema(BaseCustomerSchema):
    """Schema to validate data for customer modification (update)"""
    company_name: Optional[str] = Field(None, max_length=255, description="Company name")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name of the customer")
    phone_number: Optional[Annotated[str,
                                     StringConstraints(min_length=10, max_length=15)]
                           ] = Field(None, description="Phone number")
    contact_sales_id: Optional[int] = Field(None, description="ID of the sales contact responsible of this customer")
