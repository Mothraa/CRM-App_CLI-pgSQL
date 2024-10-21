from sqlalchemy.orm import Session

# main
from .repositories.user_repository import UserRepository
from .services.user_service import UserService
from .services.token_service import TokenManager
from .controllers.main_controller import MainController
# customer
from .repositories.customer_repository import CustomerRepository
from .services.customer_service import CustomerService
from .controllers.customer_controller import CustomerController


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


def get_token_manager() -> TokenManager:
    """create an instance of TokenManager"""
    return TokenManager()


def init_main_controller(session: Session):
    """Create the MainController injecting the session SQLAlchemy and services"""
    user_service = get_user_service(session)
    token_manager = get_token_manager()
    return MainController(user_service, token_manager)


def init_customer_controller(session: Session):
    """Create an instance of CustomerController"""
    customer_service = get_customer_service(session)
    return CustomerController(customer_service)
