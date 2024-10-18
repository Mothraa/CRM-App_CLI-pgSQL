
from my_app.models import User
from my_app.repositories.user_repository import UserRepository
from my_app.services.user_service import UserService
from my_app.exceptions import AuthenticationError
from my_app.services.token_service import TokenManager


class MainController:

    def __init__(self, session_local):
        """
        param :
            session_local : session SQLAlchemy
        """
        self.session = session_local
        self.user_repository = UserRepository(self.session)
        self.user_service = UserService(self.session, self.user_repository)
        self.token_manager = TokenManager()
        # init, pas encore d'utilisateur authentifié
        self.authenticated_user = None

    def authenticate_user_controller(self, email, password):
        """Authenticate user and stock it in the controller"""
        try:
            user = self.user_service.authenticate_user(email, password)
            self.authenticated_user = user  # on stock l'utilisateur authentifié
            # on génère les JWT
            access_token = self.token_manager.generate_access_token(user.id)
            refresh_token = self.token_manager.generate_refresh_token(user.id)
            # sauvegarde des tokens dans un fichier yaml
            self.token_manager.save_tokens(access_token, refresh_token)

            return user

        except AuthenticationError as e:
            raise AuthenticationError(f"Échec de l'authentification : {e}")
        except Exception as e:
            raise Exception(f"Une erreur inattendue s'est produite : {e}")

    def is_authenticated(self) -> bool:
        """Verify if a user is authentificated"""
        return self.authenticated_user is not None

    def get_authenticated_user(self) -> None | User:
        """Return the authentificated user"""
        return self.authenticated_user
