import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session

src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from my_app.services.user_service import UserService

# Pour activer l'option echo de SQLAlchemy (affichage du SQL, très verbeux)
ECHO = False


class TestAccounts:
    def __init__(self):
        load_dotenv(override=True)
        self.DATABASE_ADMIN_USER = os.getenv("DATABASE_APP_USER")
        self.DATABASE_ADMIN_PASSWORD = os.getenv("DATABASE_APP_PASSWORD")
        self.DATABASE_HOST = os.getenv("DATABASE_HOST")
        self.DATABASE_PORT = os.getenv("DATABASE_PORT")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME")
        self.DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")
        self.SSL_MODE = os.getenv("SSL_MODE")

        # URL pour psycopg2 (utilisé pour la connexion)
        self.new_psycopg2_url_object = URL.create(
            "postgresql+psycopg2",
            username=self.DATABASE_ADMIN_USER,
            password=self.DATABASE_ADMIN_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
            query={"sslmode": self.SSL_MODE}
        )

    def create_test_accounts(self):
        """Create test user accounts (one for each role)"""
        engine = create_engine(self.new_psycopg2_url_object, echo=ECHO, future=True)

        # Création des comptes de test dans une session
        with Session(engine) as session:
            # note : création de la session dans un context pour ne pas avoir besoin de la fermer
            try:
                user_service = UserService(session)
                user_service.create_test_accounts()
                session.commit()
                print("Création des comptes de test => OK")
            except Exception as e:
                session.rollback()
                print(f"Erreur lors de la création des comptes de test : {e}")


if __name__ == "__main__":
    test_accounts = TestAccounts()
    test_accounts.create_test_accounts()
