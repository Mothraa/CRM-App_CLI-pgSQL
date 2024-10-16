import re
import string
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from my_app.models import RoleType


class UserAddSchema(BaseModel):
    """Schema to validate data for user creation (add)"""
    email: EmailStr
    # contraintes de longueurs supplémentaire par rapport au model
    password: str = Field(min_length=12, description="Password must have minimum 12 characters")
    first_name: str = Field(max_length=100, description="First name can't exceed 100 characters")
    last_name: str = Field(max_length=100, description="Last name can't exceed 100 characters")
    last_name: str
    role: RoleType
    # les champs dates sont gérés par sqlalchemy / le model

    # contraintes supplémentaires sur le mot de passe
    @field_validator('password')
    def check_password_complexity(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase caracter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase character")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(f"[{re.escape(string.punctuation)}]", value):
            raise ValueError(f"Password must contain at least one special character : {string.punctuation}")
        return value

    model_config = {
        # permet de passer une session sqlalchemy a pydantic, utile dans le cas de serialisation d'objets ORM
        "from_attributes": True,
        # permet l'utilisation des nom d'attribut du model en plus des alias de champ pydantic
        "populate_by_name": True
    }


class UserUpdateSchema(BaseModel):
    """Schema to validate data for user modification (update)"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=12, description="Password must have a minimum of 12 characters")
    first_name: Optional[str] = Field(None, max_length=100, description="First name can't exceed 100 characters")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name can't exceed 100 characters")
    role: Optional[RoleType] = None

    model_config = {
        # permet de passer une session sqlalchemy a pydantic, utile dans le cas de serialisation d'objets ORM
        "from_attributes": True,
        # permet l'utilisation des nom d'attribut du model en plus des alias de champ pydantic
        "populate_by_name": True
    }
