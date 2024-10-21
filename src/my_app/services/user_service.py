from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from my_app.repositories.user_repository import UserRepository
from my_app.models import User
from my_app.schemas.user_schemas import UserAuthSchema, UserAddSchema, UserUpdateSchema
from my_app.permissions import has_permission  # , has_any_permission, has_all_permission
from my_app.exceptions import UserNotFoundError, InvalidPasswordError


class UserService:
    def __init__(self, session: Session, user_repository: UserRepository):
        """
        Services to create and manage users accounts
        param :
            session => the SQLAlchemy session to manage the database
            user_repository => repository to manage user data/sqlalchemy operations
        """
        self.session = session  # pas utilisé pour le moment
        self.user_repository = user_repository
        # initialisation du hachage de mot de passe avec Argon2 via argon2-cffi
        self.ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Password Hashing using Argon2-cffi"""
        return self.ph.hash(password)

    def verify_password(self, hashed_password: str, plain_password: str) -> bool:
        """For verify a password and his hash, return a boolean"""
        try:
            return self.ph.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    def get_user_by_id(self, user_id: int):
        """Retrieve a User by his ID"""
        user = self.user_repository.get_by_id(user_id)  # Appel au repository
        if not user:
            raise UserNotFoundError(f"Pas d'utilisateur avec l'ID : {user_id}")
        return user

    def authenticate_user(self, user_email, password):
        """Authenticate user, return User instance if OK, or None"""
        # On valide le format des données d'entrée avec Pydantic
        UserAuthSchema(email=user_email, password=password)

        user = self.user_repository.get_by_email(user_email)
        # user = self.user_repository.get_by_email(self.session, user_email)
        if user is None:
            raise UserNotFoundError(f"Pas d'utilisateur avec l'email : {user_email}")

        if not self.verify_password(user.password_hash, password):
            raise InvalidPasswordError("Password invalid")

        return user  # on retourne l'utilisateur si le mot de passe est OK

    def add_user(self, user_data: dict, current_user: User) -> User:
        """Method to add a new user. Hash the given password"""
        # on regarde si l'utilisateur courant a la permission de créer un compte.
        has_permission(current_user, 'add-user')  # lève une exception si NOK

        # On valide les données d'entrée avec Pydantic
        user_add = UserAddSchema(**user_data)

        # Vérifier si l'email est déjà utilisé (contrainte d'unicité du model)
        if self.user_repository.get_by_email(user_add.email):
            raise ValueError("Email is already used")

        # hashage (+salage) du password
        hashed_password = self.hash_password(user_add.password)

        # conversion de l'objet validé Pydantic en dictionnaire
        user_add_dict = user_add.model_dump()
        # on remplace le champ "password" par son hash (champ "password_hash") pour correspondre au model
        user_add_dict["password_hash"] = hashed_password
        del user_add_dict["password"]

        # creation d'un utilisateur via le repository
        new_user = self.user_repository.add(User(**user_add_dict))
        return new_user

    def update_user(self, user_id: int, update_data: dict, current_user: User) -> User:
        """Method to update an existing user, need "update-user" permission
        param :
            user_id : the id of the user to update
            update_data : ...
            current_user : active authentified current user
        """
        # on regarde si l'utilisateur courant a la permission de mettre à jour un compte.
        has_permission(current_user, "update-user")  # lève une exception si NOK

        # On valide les données d'entrée avec Pydantic
        user_update = UserUpdateSchema(**update_data)

        # On récupère l'utilisateur à mettre à jour
        user_to_update = self.user_repository.get_by_id(user_id)

        # Si un nouveau password est fourni, on regarde les permissions et on le hache
        if "password" in update_data:
            hashed_password = self.hash_password(user_update.password)
            update_data["password_hash"] = hashed_password
            del update_data["password"]

        # on applique le reste des modifications ;
        # exclude_unset : on ne retourne pas les champs qui n'ont pas été mis à jour
        for key, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user_to_update, key, value)

        # on sauvegarde les modifs
        updated_user = self.user_repository.update(user_to_update)
        return updated_user

    def delete_user(self, user_id: int, current_user: User):
        """Delete a User by his ID"""
        # on regarde si l'utilisateur courant a la permission de supprimer un compte.
        has_permission(current_user, "delete-user")  # lève une exception si NOK
        # On récupère l'utilisateur à supprimer
        user_to_delete = self.user_repository.get_by_id(user_id)

        # ...rien a valider du coté de pydantic...

        user_to_delete = self.user_repository.get_by_id(user_id)
        self.user_repository.delete(user_to_delete)
        # on ne retourne rien, par cohérence avec le repository et pour ne pas exposer les données
