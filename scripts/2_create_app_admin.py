import os
import re
import sys

from getpass import getpass
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

# on inclus 'src' dans le PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from my_app.models import RoleType, User
from my_app.services.user_service import UserService
from my_app.repositories.user_repository import UserRepository

# Pour activer l'option echo de SQLAlchemy (affichage du SQL, très verbeux)
ECHO = False

# Regex pour vérifier l'absence de caractères spéciaux
USERNAME_REGEX = r"^[a-zA-Z0-9_]+$"  # on a le droit aux "_"
PASSWORD_REGEX = r"^[a-zA-Z0-9]+$"


class AppUserCreator:
    def __init__(self):
        self.engine = None
        # TODO : charger config_loader.py
        load_dotenv(override=True)
        self.DATABASE_HOST = os.getenv("DATABASE_HOST")
        self.DATABASE_PORT = os.getenv("DATABASE_PORT")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME")
        self.DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")
        self.SSL_MODE = os.getenv("SSL_MODE")

    def get_engine(self, username, password):
        """create the SQLAlchemy engine"""
        url_object = URL.create(
            # "postgresql+pg8000",
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
        superuser_name = input("Identifiant du superutilisateur pgsql : ")
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

            email = input("Entrer un email d'utilisateur (identifiant de l'app) : ")
            # TODO : add input control

            # TODO : utiliser un password différent pour le compte pgsql et l'app
            password = getpass("Entrer un nouveau mot de passe : ")
            if not re.match(PASSWORD_REGEX, password):
                print("Le mot de passe ne doit pas contenir de caractères spéciaux.")
                continue

            confirm_password = getpass("Confirmer le mot de passe : ")
            if password != confirm_password:
                print("Les mots de passe ne correspondent pas.")
                continue

            return username, password, email

    def check_user_exists(self, username):
        """Check if a PostgreSQL user exists"""
        try:
            with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                result = conn.execute(text(f"SELECT 1 FROM pg_roles WHERE rolname = '{username}';")).fetchone()
                if result:
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Erreur lors de la vérification de l'utilisateur '{username}' : {e}")
            return False

    def verify_user_password(self, username, password):
        """Verify if the username and password are correct (try a connection)"""
        try:
            # Tentative de connexion avec le nom d'utilisateur et le mot de passe fournis
            test_url = URL.create(
                "postgresql+pg8000",
                username=username,
                password=password,
                host=self.DATABASE_HOST,
                port=self.DATABASE_PORT,
                database=self.DATABASE_NAME,
            )
            test_engine = create_engine(test_url, echo=ECHO, future=True)
            # test de connexion basique
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"Erreur de connexion '{username}' : {e}")
            return False

    def create_user(self, session, new_user_username, new_user_password):
        """Create a user"""
        try:
            with session.begin():
                session.execute(text(f"CREATE USER \"{new_user_username}\" WITH PASSWORD '{new_user_password}';"))
                print(f"Création du compte : '{new_user_username}' => OK")
        except Exception as e:
            print(f"Erreur lors de la création du compte '{new_user_username}' : {e}")

    def create_admin_in_app(self, session, new_user_email, new_user_username, new_user_password):
        """Create an admin user in the app (User table)"""
        try:
            user_repository = UserRepository(session)
            user_service = UserService(session, user_repository)

            # Hash du mdp
            hashed_password = user_service.hash_password(new_user_password)

            with session.begin():
                # Création de l'utilisateur admin dans la table User de l'application
                new_user = User(
                    email=new_user_email,
                    password_hash=hashed_password,
                    first_name=new_user_username,
                    role=RoleType.admin
                )
                session.add(new_user)
                print(f"Admin '{new_user_email}' créé dans la table User de l'application")

        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur admin dans l'application : {e}")

    def grant_privileges(self, session, username):
        """Grant privileges to the user account and restricted access to schema"""
        try:
            with session.begin():
                # accede uniquement au schema, sur des opérations CRUD
                session.execute(text(
                    f"GRANT USAGE ON SCHEMA {self.DATABASE_SCHEMA} TO {username};"
                ))
                # donne tous les privilèges sur toutes les tables du schema
                session.execute(text(
                    f"GRANT SELECT, INSERT, UPDATE, DELETE"
                    f" ON ALL TABLES IN SCHEMA {self.DATABASE_SCHEMA} TO {username};"
                ))

                # donne tous les privilèges sur toutes les tables FUTURES du schema ("ALTER DEFAULT")
                session.execute(text(
                    f"ALTER DEFAULT PRIVILEGES IN SCHEMA {self.DATABASE_SCHEMA}"
                    f" GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {username};"
                ))

                # on donne l'acces d'usage et de select sur toutes les sequences (mais sans pouvoir les modifier)
                session.execute(text(
                    f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA {self.DATABASE_SCHEMA} TO {username};"
                ))
                session.execute(text(
                    f"ALTER DEFAULT PRIVILEGES IN SCHEMA {self.DATABASE_SCHEMA}"
                    f" GRANT USAGE, SELECT ON SEQUENCES TO {username};"
                ))

                # revoque les privileges sur les autres schemas (que public dans notre cas d'usage ici)
                session.execute(text(f"REVOKE ALL ON SCHEMA public FROM {username};"))

                print(f'Les privilèges ont été appliqués pour "{username}" sur le schéma "{self.DATABASE_SCHEMA}"')
        except Exception as e:
            print(f"Erreur d'attribution des privilèges pour '{username}' : {e}")


if __name__ == "__main__":
    app_user_creator = AppUserCreator()

    # demande le nom et le mot de passe du superuser
    superuser_name, superuser_password = app_user_creator.request_superuser_access()

    # Création d'un engine avec le superuser
    app_user_creator.get_engine(superuser_name, superuser_password)
    Session = sessionmaker(bind=app_user_creator.engine)
    session = Session()

    # Demande des informations pour créer l'utilisateur
    new_user_username, new_user_password, new_user_email = app_user_creator.request_user_infos()

    # Création du compte pgsql
    if not app_user_creator.check_user_exists(new_user_username):
        app_user_creator.create_user(session, new_user_username, new_user_password)
        app_user_creator.grant_privileges(session, new_user_username)
    else:
        print(f"L'utilisateur PostgreSQL '{new_user_username}' existe déjà.")
        # si le mdp saisi ne correspond pas, on arrete le script
        if not app_user_creator.verify_user_password(new_user_username, new_user_password):
            print("Le mot de passe indiqué ne correspond pas a l'utilisateur existant.\
                   Merci de créer un autre utilisateur.")
            sys.exit(1)

        # si le mdp indiqué est correct on demande confirmation pour la modification des privilèges
        confirmation = input(f"Etes vous sur de vouloir modifier les privilèges de '{new_user_username}' ? (y/n): ")

        if confirmation.lower() == 'y':
            app_user_creator.grant_privileges(session, new_user_username)
            print(f"Privilèges modifiés pour '{new_user_username}'.")
        else:
            print("Modification des privilèges annulée.")

    # creation de l'utilisateur dans la table User de l'application
    app_user_creator.create_admin_in_app(session, new_user_email, new_user_username, new_user_password)
