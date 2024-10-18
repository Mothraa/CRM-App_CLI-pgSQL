import re
import string
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from my_app.models import RoleType


class BaseUserSchema(BaseModel):
    """
    Base schema with common validators :
        - email validation (format and domaine restriction)
        - ...
    """

    email: EmailStr

    # TODO : activer cette contrainte, nécessite d'uniformiser le domaine (avec les comptes tests notamment)
    # @field_validator('email')
    # def check_email(cls, value):
    #     if not value.endswith("@mondomaine.com"):
    #         raise ValueError("Email domain must be '@mondomaine.com'")
    #     return value

    model_config = {
        # permet de passer une session sqlalchemy a pydantic, utile dans le cas de serialisation d'objets ORM
        "from_attributes": True,
        # permet l'utilisation des nom d'attribut du model en plus des alias de champ pydantic
        "populate_by_name": True
    }


class PasswordValidationSchema(BaseModel):

    password: str = Field(min_length=12, description="Password must have minimum 12 characters")

    # contraintes de complexité sur le mot de passe en plus de la longueur
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


class UserAuthSchema(BaseUserSchema):
    """Schema to validate data for user authentication
        inherits from :
        - class BaseUserSchema for email validation
    """
    email: EmailStr

    # pas de validation de format de mot de passe, pourrait poser problème en cas d'évolution des règles\
    # pour les anciens utilisateurs (ou mecanisme d'update du mdp a implémenter).


class UserAddSchema(BaseUserSchema, PasswordValidationSchema):
    """
    Schema to validate data for user creation (add)
    inherits from :
        - class BaseUserSchema for email validation
        - PasswordValidationSchema for password validation
    """
    # contraintes de longueurs supplémentaire par rapport au model
    first_name: str = Field(max_length=100, description="First name can't exceed 100 characters")
    last_name: str = Field(max_length=100, description="Last name can't exceed 100 characters")
    role: RoleType
    # les champs dates sont gérés par sqlalchemy / le model

    model_config = {
        # permet de passer une session sqlalchemy a pydantic, utile dans le cas de serialisation d'objets ORM
        "from_attributes": True,
        # permet l'utilisation des nom d'attribut du model en plus des alias de champ pydantic
        "populate_by_name": True
    }


class UserUpdateSchema(BaseUserSchema, PasswordValidationSchema):
    """
    Schema to validate data for user modification (update)
    inherits from :
        - class BaseUserSchema for email validation
        - PasswordValidationSchema for password validation
    """
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100, description="First name can't exceed 100 characters")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name can't exceed 100 characters")
    role: Optional[RoleType] = None
