
from cryptography.fernet import Fernet
from my_app.config_loader import DATA_ENCRYPTION_KEY

fernet = Fernet(DATA_ENCRYPTION_KEY)


def encrypt(data: str) -> str:
    """Encrypt data"""
    return fernet.encrypt(data.encode()).decode()


def decrypt(encrypted_data: str) -> str:
    """Decrypt data"""
    return fernet.decrypt(encrypted_data.encode()).decode()
