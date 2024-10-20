from sqlalchemy.orm import Session

from .repositories.user_repository import UserRepository
from .services.user_service import UserService
from .services.token_service import TokenManager
from .controllers.main_controller import MainController


def get_user_service(session: Session):
    """create an instance of UserService"""
    # Injection du repository dans le service
    # on injecte la session SQLAlchemy dans le UserRepository pour qu'il puisse interagir avec la base de données.
    # Le UserRepository est un objet qui encapsule l'accès aux données pour les entités User.
    # Le repository a besoin d'une session SQLAlchemy pour fonctionner.
    user_repository = UserRepository(session)
    return UserService(session, user_repository)


def get_token_manager() -> TokenManager:
    """create an instance of TokenManager"""
    return TokenManager()


def init_main_controller(session: Session):
    """Create the MainController injecting the session SQLAlchemy and services"""
    user_service = get_user_service(session)
    token_manager = get_token_manager()
    return MainController(user_service, token_manager)
