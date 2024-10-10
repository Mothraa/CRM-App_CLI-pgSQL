import os
import re
from getpass import getpass
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text

# Pour activer l'option echo de SQLAlchemy (affichage du SQL, très verbeux)
ECHO = False

# Regex pour vérifier l'absence de caractères spéciaux
USERNAME_REGEX = r"^[a-zA-Z0-9_]+$"  # on a le droit aux "_"
PASSWORD_REGEX = r"^[a-zA-Z0-9]+$"


class AppUserCreator:
    def __init__(self):
        self.engine = None
        load_dotenv(override=True)
        self.DATABASE_HOST = os.getenv("DATABASE_HOST")
        self.DATABASE_PORT = os.getenv("DATABASE_PORT")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME")
        self.DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")
        self.SSL_MODE = os.getenv("SSL_MODE")

    def get_engine(self, username, password):
        """create the SQLAlchemy engine (with psycopg2)"""
        url_object = URL.create(
            "postgresql+psycopg2",
            username=username,
            password=password,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
            query={"sslmode": self.SSL_MODE},
        )
        self.engine = create_engine(url_object, echo=ECHO, future=True)

    def request_superuser_access(self):
        """Prompt to ask name and password of superuser"""
        superuser_name = input("Entrer le nom du superutilisateur PostgreSQL afin de créer une nouvelle base : ")
        superuser_password = getpass("Mot de passe : ")
        return superuser_name, superuser_password

    def request_user_infos(self):
        """Prompt the user to enter the new username and password"""
        print("Création du nouveau compte : ")
        while True:
            username = input("Entrer un nom d'utilisateur à créer : ")
            if not re.match(USERNAME_REGEX, username):
                print("Le nom d'utilisateur ne doit pas contenir de caractères spéciaux.")
                continue

            password = getpass("Entrer un nouveau mot de passe : ")
            if not re.match(PASSWORD_REGEX, password):
                print("Le mot de passe ne doit pas contenir de caractères spéciaux.")
                continue

            confirm_password = getpass("Confirmer le mot de passe : ")
            if password != confirm_password:
                print("Les mots de passe ne correspondent pas.")
                continue

            return username, password

    def create_user(self, superuser_name, superuser_password, new_user_username, new_user_password):
        """Create an user"""
        self.get_engine(superuser_name, superuser_password)
        try:
            # Connexion à la base pour créer l'utilisateur le nouvel utilisateur
            with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                query = f"CREATE USER \"{new_user_username}\" WITH PASSWORD '{new_user_password}';"
                conn.execute(text(query))
                print(f"Création du compte : '{new_user_username}' => OK")
        except Exception as e:
            print(f"Erreur lors de la création du compte '{new_user_username}' : {e}")

    def grant_privileges(self, username):
        """Grant privileges to the user account and restricted access to schema"""
        try:
            with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                # accede uniquement au schema, sur des opérations CRUD
                conn.execute(text(
                    f"GRANT USAGE ON SCHEMA {self.DATABASE_SCHEMA} TO {username};"
                    ))
                # Grant privileges on all existing tables in the schema
                conn.execute(text(
                    f"GRANT SELECT, INSERT, UPDATE, DELETE"
                    f"ON ALL TABLES IN SCHEMA {self.DATABASE_SCHEMA} TO {username};"
                    ))

                # Grant privileges on future tables in the schema
                conn.execute(text(
                    f"ALTER DEFAULT PRIVILEGES IN SCHEMA {self.DATABASE_SCHEMA}"
                    f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {username};"
                    ))

                # Grant usage and select on sequences (but no modification rights)
                conn.execute(text(
                    f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA {self.DATABASE_SCHEMA} TO {username};"
                    ))
                conn.execute(text(
                    f"ALTER DEFAULT PRIVILEGES IN SCHEMA {self.DATABASE_SCHEMA}"
                    f"GRANT USAGE, SELECT ON SEQUENCES TO {username};"
                    ))

                # revoque les privileges sur les autres schemas (que public ici)
                conn.execute(text(f"REVOKE ALL ON SCHEMA public FROM {username};"))

                print(f'Les privilèges ont été appliqués pour "{username}" sur le schéma "{self.DATABASE_SCHEMA}"')
        except Exception as e:
            print(f"Erreur d'attribution des privilèges pour '{username}' : {e}")


if __name__ == "__main__":
    # Initialisation de la configuration
    app_user_creator = AppUserCreator()

    # Demande le nom et le mot de passe du superuser
    superuser_name, superuser_password = app_user_creator.request_superuser_access()

    # Demande des informations pour créer l'utilisateur
    new_user_username, new_user_password = app_user_creator.request_user_infos()

    # Création du compte
    app_user_creator.create_user(superuser_name, superuser_password, new_user_username, new_user_password)

    # Attribution des privilèges sur le schéma
    app_user_creator.grant_privileges(new_user_username)
