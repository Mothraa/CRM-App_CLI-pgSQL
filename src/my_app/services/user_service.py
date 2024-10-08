from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import date
from sqlalchemy.orm import Session
from my_app.models import User, RoleType

# initialisation du hachage de mot de passe avec Argon2 via argon2-cffi
ph = PasswordHasher()


class UserService:
    def __init__(self, session: Session):
        """
        Services to create and manage users accounts
        param : session => the SQLAlchemy session to manage the database
        """
        self.session = session

    def hash_password(self, password: str) -> str:
        """Password Hashing using Argon2-cffi"""
        return ph.hash(password)

    def verify_password(self, hashed_password: str, plain_password: str) -> bool:
        """For verify a password and his hash, return a boolean"""
        try:
            return ph.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    def create_user(self, email: str, password: str, first_name: str, last_name: str, role: RoleType) -> User:
        """Function to create a new user. Hash the given password"""
        hashed_password = self.hash_password(password)

        new_user = User(
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            created_at=date.today()
        )

        self.session.add(new_user)
        self.session.commit()
        return new_user

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
