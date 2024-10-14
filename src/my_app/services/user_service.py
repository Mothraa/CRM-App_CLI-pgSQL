from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from my_app.repositories.user_repository import UserRepository
from my_app.models import User, RoleType
from my_app.schemas.user_schemas import UserAddSchema, UserUpdateSchema
from my_app.permissions import has_permission  # , has_any_permission, has_all_permission


class UserService:
    def __init__(self, session: Session, user_repository: UserRepository):
        """
        Services to create and manage users accounts
        param :
            session => the SQLAlchemy session to manage the database
            user_repository => repository to manage user data/sqlalchemy operations
        """
        self.session = session
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
        """
        param :
            user_id : the id of the user to update
            update_data : ...
            current_user : active authentified current user
        """
        # on regarde si l'utilisateur courant a la permission de mettre à jour un compte.
        has_permission(current_user, 'update-user')  # lève une exception si NOK

        # On valide les données d'entrée avec Pydantic
        user_update = UserUpdateSchema(**update_data)

        # On récupère l'utilisateur à mettre à jour
        user_to_update = self.user_repository.get_by_id(user_id)

        # Si un nouveau password est fourni, on regarde les permissions et on le hache
        if "password" in update_data:
            hashed_password = self.hash_password(user_update.password)
            update_data['password_hash'] = hashed_password
            del update_data['password']

        # on applique le reste des modifications ;
        # exclude_unset : on ne retourne pas les champs qui n'ont pas été mis à jour
        for key, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user_to_update, key, value)

        # on sauvegarde les modifs
        updated_user = self.user_repository.update(user_to_update)
        return updated_user

    def delete_user(self, user_id: int, current_user: User):
        # on regarde si l'utilisateur courant a la permission de supprimer un compte.
        has_permission(current_user, 'delete-user')  # lève une exception si NOK
        # On récupère l'utilisateur à supprimer
        user_to_delete = self.user_repository.get_by_id(user_id)

        # rien a valider du coté de pydantic

        user_to_delete = self.user_repository.get_by_id(user_id)
        self.user_repository.delete(user_to_delete)
        # on ne retourne rien, par cohérence avec le repository et pour ne pas exposer les données

    # TODO : a déplacer dans seed_test_users.py une fois le validator ajouté
    def create_test_accounts(self):
        """Create a test account for each user role. ONLY FOR TEST/DEBUG, DON'T USE IN PRODUCTION"""
        # liste des utilisateurs créés retournés par la methode
        created_users = []
        try:
            roles = [RoleType.admin, RoleType.manage, RoleType.sales, RoleType.support]
            for role in roles:
                email = f"test_{role.value}@example.com"
                plain_password = f"password_{role.value}"  # Mot de passe simple pour les tests
                first_name = "Test"
                last_name = f"User_{role.value}"

                user = self.create_user(email, plain_password, first_name, last_name, role)
                created_users.append(user)
                print(f"Utilisateur de test créé : {user.email} avec le rôle {user.role}")

            return created_users

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la création des comptes de test : {e}")
            return None
