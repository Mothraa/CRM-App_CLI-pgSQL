import sys
import os
from getpass import getpass

# on inclut 'src' dans le PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from my_app.services.user_service import UserService
from my_app.repositories.user_repository import UserRepository
from my_app.db_config import get_session
from my_app.models import Customer, Contract, Event, RoleType


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


def hard_delete_all_data(session, admin_user):
    """
    Supprime définitivement toutes les données des tables Customer, Contract et Event.
    On passe directement par la session car le repository ne gère que les soft delete
    """

    try:
        events = session.query(Event).all()
        for event in events:
            session.delete(event)

        contracts = session.query(Contract).all()
        for contract in contracts:
            session.delete(contract)

        customers = session.query(Customer).all()
        for customer in customers:
            session.delete(customer)

        session.commit()  # Commit les modifications une fois que tout est supprimé
        print(f"{len(events)} Event(s) supprimés définitivement.")
        print(f"{len(contracts)} Contract(s) supprimés définitivement.")
        print(f"{len(customers)} Customer(s) supprimés définitivement.")
        print("Suppression définitive des données des tables Customer, Contract et Event => OK")

    except Exception as e:
        session.rollback()  # En cas d'erreur, annuler les modifications
        print(f"Erreur lors de la suppression des données : {e}")


if __name__ == "__main__":
    session = get_session()

    try:
        # Demande les infos d'identification admin
        email, password = prompt_admin_login()

        # init de UserService pour authentifier l'administrateur
        user_repository = UserRepository(session)
        user_service = UserService(session, user_repository)

        admin_user = authenticate_admin(user_service, email, password)
        hard_delete_all_data(session, admin_user)

    finally:
        session.close()
