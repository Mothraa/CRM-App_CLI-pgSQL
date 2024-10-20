import sys
import os
from getpass import getpass

# on inclus 'src' dans le PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from my_app.services.user_service import UserService
from my_app.repositories.user_repository import UserRepository
from my_app.db_config import get_session
from my_app.models import RoleType

# mot de passe par défaut indentique pour tous les comptes tests
DEFAULT_PASSWORD = "Super_passwordQuiR3spectLéContraintes!!"


def prompt_admin_login():
    """Prompt to authentify app admin"""
    email = input("Entrez votre email admin (compte de l'app) : ")
    password = getpass("Entrez votre mot de passe admin : ")
    return email, password


def authenticate_admin(user_service, email, password):
    """Authentify admin user"""
    try:
        admin_user = user_service.authenticate_user(email, password)
        if admin_user.role != RoleType.admin:
            print("Erreur : Cet utilisateur n'est pas admin")
            sys.exit(1)
        return admin_user
    except Exception as e:
        print(f"Erreur d'authentification : {e}")
        sys.exit(1)


def create_test_accounts(session, admin_user):
    """Créer des comptes utilisateurs pour chaque rôle de test, et les enregistrer en base de données."""

    # Initialisation du repository et du service utilisateur
    user_repository = UserRepository(session)
    user_service = UserService(session, user_repository)

    # Liste des rôles à créer pour les comptes de test
    roles = [RoleType.admin, RoleType.manage, RoleType.sales, RoleType.support]
    created_users = []

    try:
        for role in roles:
            # TODO : ajouter ces informations a l'environnement de dev (.env.development)
            email = f"{role.value}@test.com"
            password = DEFAULT_PASSWORD
            first_name = "test"
            last_name = f"user_{role.value}"

            # Encapsulation des données dans un dictionnaire
            user_data = {
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "role": role
            }

            # Création de l'utilisateur via le service avec admin_user comme current_user
            user = user_service.add_user(user_data=user_data, current_user=admin_user)
            created_users.append(user)
            print(f"Utilisateur de test créé : {user.email} avec le rôle {user.role}")

        session.commit()  # Commit les modifications une fois que tous les utilisateurs ont été créés
        print("Création des comptes utilisateurs test => OK")
        return created_users

    except Exception as e:
        session.rollback()  # En cas d'erreur, annuler les modifications
        print(f"Erreur lors de la création des comptes test : {e}")
        return None


if __name__ == "__main__":
    # Créer une session pour interagir avec la base de données via db_config
    session = get_session()

    try:
        # Demande les infos d'identification admin
        email, password = prompt_admin_login()

        # init de UserService pour authentifier l'administrateur
        user_repository = UserRepository(session)
        user_service = UserService(session, user_repository)
        admin_user = authenticate_admin(user_service, email, password)

        create_test_accounts(session, admin_user)

    finally:
        session.close()
