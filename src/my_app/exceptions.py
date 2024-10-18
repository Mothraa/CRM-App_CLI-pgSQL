
class UserNotFoundError(Exception):
    """Raised when a user is not found in the database"""
    pass


class InvalidPasswordError(Exception):
    """Raised when the password is incorrect"""
    pass


class AuthenticationError(Exception):
    """Raised for generic authentication failures"""
    pass
