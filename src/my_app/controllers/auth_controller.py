from my_app.models import User
from my_app.exceptions import InvalidPasswordError
from sentry_sdk import set_user


class MainController:

    def __init__(self, user_service, token_manager):
        """
        param :
            user_service : injecté pour gérer l'identification
            token_manager : injecté pour gérer la génération et la validation des tokens JWT
        """
        self.user_service = user_service
        self.token_manager = token_manager
        # init, pas encore d'utilisateur authentifié
        self.authenticated_user = None

    def authenticate_user_controller(self, email, password):
        """Authenticate user and stock it in the controller"""
        try:
            user = self.user_service.authenticate_user(email, password)
            self.authenticated_user = user  # on stock l'utilisateur authentifié

            # on ajoute l'utilisateur au contexte sentry
            set_user({"id": user.id, "email": user.email})

            # on génère les JWT
            access_token = self.token_manager.generate_access_token(user.id)
            refresh_token = self.token_manager.generate_refresh_token(user.id)
            # sauvegarde des tokens dans un fichier yaml
            self.token_manager.save_tokens(access_token, refresh_token)
            return user
        except InvalidPasswordError:
            # Retourner None pour indiquer un échec d'authentification
            return None
        # les autres exceptions sont capturées a un plus haut niveau

    def verify_and_refresh_token(self):
        """Verify the token and refresh if necessary"""
        try:
            # Charger les tokens depuis le fichier
            tokens = self.token_manager.load_tokens()

            if not tokens:
                return None  # si pas de token

            # On verifie le token d'accès
            access_token = tokens.get('access_token')
            decoded_token = self.token_manager.verify_token(access_token)
            # authentification OK, on récupère l'utilisateur
            if decoded_token:
                return self._fetch_user_from_token(decoded_token)

            # si l'access token a expiré, on tente un refresh
            refresh_token = tokens.get('refresh_token')
            if not refresh_token:
                return None  # si pas de refresh token

            # on vérifie si le refresh token est encore valide
            decoded_refresh_token = self.token_manager.verify_token(refresh_token)
            if not decoded_refresh_token:
                return None  # si invalide ou expiré

            # on génère un nouveau access token
            new_access_token = self.token_manager.refresh_access_token(refresh_token)
            if new_access_token:
                # on savegarde avec le nouveau access token
                self.token_manager.save_tokens(new_access_token, refresh_token)
                # authentification OK, on récupère l'utilisateur
                decoded_token = self.token_manager.verify_token(new_access_token)
                return self._fetch_user_from_token(decoded_token)
            return None
        except Exception as e:
            raise Exception(f"Erreur de vérification des tokens : {e}")

    def is_authenticated(self) -> bool:
        """Verify if a user is authentificated"""
        return self.authenticated_user is not None

    def get_authenticated_user(self) -> None | User:
        """Return the authentificated user"""
        return self.authenticated_user

    def _fetch_user_from_token(self, decoded_token):
        """Fetch the User from his token"""
        user_id = decoded_token["user_id"]
        user = self.user_service.get_by_id(user_id)
        self.authenticated_user = user
        return user

    def logout(self):
        """Logout the user and delete tokens"""
        # si nécessaire, réinit l'utilisateur authentifié
        if self.authenticated_user:
            self.authenticated_user = None
        # on efface l'utilisateur du contexte sentry
        set_user(None)
        # Supprime le fichier de tokens et retourne un bool
        return self.token_manager.delete_tokens()
