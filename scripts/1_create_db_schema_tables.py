import os
import sys
from getpass import getpass
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, inspect
from sqlalchemy.schema import CreateSchema
from sqlalchemy_utils import database_exists, create_database

# Chemin vers le dossier 'src' contenant les modèles
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from my_app.models import Base

# Pour activer l'option echo de SQLAlchemy (affichage du SQL, très verbeux)
ECHO = False


class DatabaseInit:
    def __init__(self):
        self.engine = None
        # TODO : charger config_loader.py
        load_dotenv(override=True)
        self.DATABASE_ADMIN_USER = os.getenv("DATABASE_ADMIN_USER")
        self.DATABASE_ADMIN_PASSWORD = os.getenv("DATABASE_ADMIN_PASSWORD")
        self.DATABASE_HOST = os.getenv("DATABASE_HOST")
        self.DATABASE_PORT = os.getenv("DATABASE_PORT")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME")
        self.DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")
        self.SSL_MODE = os.getenv("SSL_MODE")

    def get_engine(self, engine=None, username=None, password=None, database=None):
        """create the SQLAlchemy engine
        param : engine values :  psycopg2 by default, pg8000 (pour creation base et schema)"""
        if not engine or engine == "psycopg2":
            driver_name = "postgresql+psycopg2"
            query_params = {"sslmode": self.SSL_MODE}
        else:
            driver_name = "postgresql+" + engine
            query_params = {}
        if not database:
            database = self.DATABASE_NAME
        if not username:
            username = self.DATABASE_ADMIN_USER
        if not password:
            password = self.DATABASE_ADMIN_PASSWORD
        url_object = URL.create(
            driver_name,
            username=username,
            password=password,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=database,
            query=query_params,
        )
        self.engine = create_engine(url_object, echo=ECHO, future=True)

    def request_superuser_access(self):
        """Prompt to ask name and password of superuser (for creating new db)"""
        superuser_name = input("Entrer le nom du superutilisateur PostgreSQL afin de créer une nouvelle base : ")
        superuser_password = getpass("Mot de passe : ")
        return superuser_name, superuser_password

    def create_new_db(self, superuser_name, superuser_password):
        """create database with psycopg2 driver and SQLAlchemy-Utils"""
        self.get_engine(engine="pg8000", username=superuser_name, password=superuser_password, database="postgres")

        # Création de l'URL pour la base cible (projet12)
        new_db_url = URL.create(
            "postgresql+pg8000",
            username=superuser_name,
            password=superuser_password,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
        )

        try:
            # Vérification si la base de données existe déjà
            if not database_exists(new_db_url):
                # sinon on la crée
                create_database(new_db_url)
                print(f"Création de la base {self.DATABASE_NAME} => OK")
            else:
                print(f"La base {self.DATABASE_NAME} existe déjà")
        except Exception as e:
            print(f"Erreur lors de la création de la base {self.DATABASE_NAME} : {e}")

    def create_schema(self, superuser_name, superuser_password):
        """create schema with superuser account"""
        self.get_engine(username=superuser_name, password=superuser_password)

        try:
            # Connexion à la base nouvellement créée pour créer le schéma
            with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
                inspector = inspect(connection)
                # Vérification de l'existence du schéma
                if not inspector.has_schema(self.DATABASE_SCHEMA):
                    connection.execute(CreateSchema(self.DATABASE_SCHEMA, if_not_exists=True))
                    print(f"Création du schéma '{self.DATABASE_SCHEMA}' => OK")
                else:
                    print(f"Le schéma '{self.DATABASE_SCHEMA}' existe déjà")
        except Exception as e:
            print(f"Erreur lors de la création du schéma '{self.DATABASE_SCHEMA}' : {e}")

    def create_tables(self, base, superuser_name, superuser_password):
        """Create tables with SQLAlchemy"""
        self.get_engine(username=superuser_name, password=superuser_password)
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names(schema=self.DATABASE_SCHEMA)

            # on compare les tables à ajouter avec celles déjà existantes
            tables_to_create = []
            tables_already_existing = []
            for table in base.metadata.tables.values():
                if table.name in existing_tables:
                    tables_already_existing.append(table.name)
                else:
                    tables_to_create.append(table)

            if tables_already_existing:
                print(f"Ces tables doivent être créées mais existent déjà : {tables_already_existing}")

            # on crée les tables manquantes
            if tables_to_create:
                with self.engine.begin() as connection:
                    base.metadata.create_all(connection, tables=tables_to_create)
                    print(f"Création des tables : {[table.name for table in tables_to_create]} => OK")
            else:
                print("Toutes les tables existent déjà.")
        except Exception as e:
            print(f"Erreur lors de la création des tables : {e}")


if __name__ == "__main__":
    # Initialisation de la configuration
    db_init = DatabaseInit()

    # Demande le nom et le mot de passe du superuser (en vue de créer une nouvelle base)
    superuser_name, superuser_password = db_init.request_superuser_access()

    # Création de la base avec psycopg2 et le compte superuser
    db_init.create_new_db(superuser_name, superuser_password)

    # Création du schema avec le superuser
    db_init.create_schema(superuser_name, superuser_password)

    # Création des tables dans le schéma spécifié par le superuser
    db_init.create_tables(Base, superuser_name, superuser_password)
