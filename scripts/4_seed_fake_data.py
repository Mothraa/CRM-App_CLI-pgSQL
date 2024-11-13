import sys
import os
from getpass import getpass
import random
from faker import Faker

# on inclut 'src' dans le PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from my_app.services.user_service import UserService
from my_app.repositories.user_repository import UserRepository
from my_app.repositories.customer_repository import CustomerRepository
from my_app.repositories.contract_repository import ContractRepository
from my_app.repositories.event_repository import EventRepository
from my_app.db_config import get_session
from my_app.models import RoleType, ContractStatus, Customer, Contract, Event
from my_app.utils.encryption_utils import encrypt

# nombre d'entités a générer par table
NB_OF_ENTITIES = 10


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


def create_test_data(session, admin_user, faker):
    """Création des clients, contrats et événements de test"""
    customer_repository = CustomerRepository(session)
    contract_repository = ContractRepository(session)
    event_repository = EventRepository(session)

    created_customers = []
    created_contracts = []
    created_events = []

    try:
        for _ in range(NB_OF_ENTITIES):

            fake_full_name = faker.name()
            first_name, last_name = fake_full_name.split()[:2]
            first_name = first_name.lower()
            last_name = last_name.lower()
            fake_email = f"{first_name}.{last_name}@fake.com"

            customer_data = {
                "company_name": encrypt(faker.company()),
                "full_name": encrypt(fake_full_name),
                "email": encrypt(fake_email),
                "phone_number": encrypt(faker.phone_number()),
                "contact_sales_id": admin_user.id
            }
            customer = Customer(**customer_data)
            customer_repository.add(customer)
            created_customers.append(customer)

            contract_data = {
                "customer_id": customer.id,
                "contact_sales_id": admin_user.id,
                "total_amount": round(random.uniform(5000, 50000), 2),
                "remaining_amount": round(random.uniform(100, 4999), 2),
                "status": random.choice(list(ContractStatus))
            }
            contract = Contract(**contract_data)
            contract_repository.add(contract)
            created_contracts.append(contract)

            event_data = {
                "name": f"Séminaire : {faker.catch_phrase()}",
                "location": faker.city(),
                "start_date": faker.date_time_between(start_date="now", end_date="+10d"),
                "end_date": faker.date_time_between(start_date="+11d", end_date="+14d"),
                "attendees": str(random.randint(50, 500)),
                "comments": None,
                "contract_id": contract.id,
                "contact_support_id": admin_user.id
            }
            event = Event(**event_data)
            event_repository.add(event)
            created_events.append(event)

            print(f"Client: {customer.full_name} ; {contract.status} ; {event.name}")

        session.commit()  # Commit les modifications une fois que tout est créé
        print(f"Création de {NB_OF_ENTITIES} données de test => OK")

    except Exception as e:
        session.rollback()  # En cas d'erreur, annuler les modifications
        print(f"Erreur lors de la création des données de test : {e}")


if __name__ == "__main__":
    session = get_session()
    faker = Faker('fr_FR')

    try:
        # Demande les infos d'identification admin
        email, password = prompt_admin_login()

        # init de UserService pour authentifier l'administrateur
        user_repository = UserRepository(session)
        user_service = UserService(session, user_repository)
        admin_user = authenticate_admin(user_service, email, password)

        create_test_data(session, admin_user, faker)
    finally:
        session.close()
