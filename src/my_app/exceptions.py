
class UserNotFoundError(Exception):
    """Raised when a user is not found in the database"""
    def __init__(self, message="Erreur, utilisateur non trouvé"):
        self.message = message
        super().__init__(self.message)


class InvalidPasswordError(Exception):
    """Raised when the password is incorrect"""
    def __init__(self, message="Erreur, mot de passe invalide"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    """Raised for generic authentication erros"""
    def __init__(self, message="Erreur d'authentification"):
        self.message = message
        super().__init__(self.message)


class LogoutError(Exception):
    """Raised for errors during logout"""
    def __init__(self, message="Erreur lors de la déconnexion"):
        self.message = message
        super().__init__(self.message)


# token_service
class TokenDeleteError(Exception):
    """Raised for errors when delete token file"""
    def __init__(self, message, file_path):
        self.message = message
        self.file_path = file_path
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.file_path}"


# customer_service
class CustomerNotFoundError(Exception):
    """Raised when a customer is not found in db"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"CustomerNotFoundError: {self.message}"
