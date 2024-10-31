from sqlalchemy.orm import Session

# main
from .services.token_service import TokenManager
from .controllers.auth_controller import MainController
# user
from .repositories.user_repository import UserRepository
from .services.user_service import UserService
from .controllers.user_controller import UserController
# customer
from .repositories.customer_repository import CustomerRepository
from .services.customer_service import CustomerService
from .controllers.customer_controller import CustomerController
# contract
from .repositories.contract_repository import ContractRepository
from .services.contract_service import ContractService
from .controllers.contract_controller import ContractController
# event
from .repositories.event_repository import EventRepository
from .services.event_service import EventService
from .controllers.event_controller import EventController


def get_user_service(session: Session):
    """create an instance of UserService"""
    # Injection du repository dans le service
    # on injecte la session SQLAlchemy dans le UserRepository pour qu'il puisse interagir avec la base de données.
    # Le UserRepository est un objet qui encapsule l'accès aux données pour les entités User.
    # Le repository a besoin d'une session SQLAlchemy pour fonctionner.
    user_repository = UserRepository(session)
    return UserService(session, user_repository)


def get_customer_service(session: Session):
    """create an instance of CustomerService"""
    customer_repository = CustomerRepository(session)
    return CustomerService(session, customer_repository)


def get_contract_service(session: Session):
    """create an instance of ContractService"""
    contract_repository = ContractRepository(session)
    return ContractService(session, contract_repository)


def get_event_service(session: Session):
    """create an instance of EventService"""
    event_repository = EventRepository(session)
    return EventService(session, event_repository)


def get_token_manager() -> TokenManager:
    """create an instance of TokenManager"""
    return TokenManager()


def init_main_controller(session: Session):
    """Create the MainController injecting the session SQLAlchemy and services"""
    user_service = get_user_service(session)
    token_manager = get_token_manager()
    return MainController(user_service, token_manager)


def init_user_controller(session: Session):
    """Create an instance of UserController"""
    user_service = get_user_service(session)
    return UserController(user_service)


def init_customer_controller(session: Session):
    """Create an instance of CustomerController"""
    customer_service = get_customer_service(session)
    user_service = get_user_service(session)
    return CustomerController(customer_service, user_service)


def init_contract_controller(session: Session):
    """Create an instance of ContractController"""
    contract_service = get_contract_service(session)
    return ContractController(contract_service)


def init_event_controller(session: Session):
    """Create an instance of EventController"""
    event_service = get_event_service(session)
    contract_service = get_contract_service(session)
    user_service = get_user_service(session)
    return EventController(event_service, contract_service, user_service)
