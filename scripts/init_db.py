import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, inspect
from sqlalchemy.schema import CreateSchema
# from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

# from my_app.services.user_service import UserService
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from my_app.models import Base


# Pour activer l'option echo de SQLAlchemy (affichage du SQL, très verbeux)
ECHO = False


class DatabaseInit:
    def __init__(self):
        load_dotenv()
        self.DATABASE_USER = os.getenv("DATABASE_USER")
        self.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
        self.DATABASE_HOST = os.getenv("DATABASE_HOST")
        self.DATABASE_PORT = os.getenv("DATABASE_PORT")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME")
        self.DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")

        # URL pour psycopg2 (utilisé pour les schémas et les tables)
        self.new_psycopg2_url_object = URL.create(
            "postgresql+psycopg2",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
        )

    def create_new_db(self):
        """create database with pg8000 driver and SQLAlchemy-Utils"""
        # URL pour la connexion à la base postgres par défaut (utile pour créer une nouvelle base)
        default_url_object = URL.create(
            "postgresql+pg8000",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database="postgres",
        )

        # URL de la nouvelle base (utile pour tester si elle existe déjà ou non)
        new_db_pg8000_url_object = URL.create(
            "postgresql+pg8000",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
        )

        try:
            # Vérification si la base de données existe déjà
            # on se "connecte" à la base existante postgres
            create_engine(default_url_object)
            # on regarde ensuite si la base que l'on souhaite créé existe déjà
            if not database_exists(new_db_pg8000_url_object):
                # sinon on la créé
                create_database(new_db_pg8000_url_object)
                print(f"Création de la base {self.DATABASE_NAME} => OK")
            else:
                print(f"La base {self.DATABASE_NAME} existe déjà")
        except Exception as e:
            print(f"Erreur lors de la création de la base {self.DATABASE_NAME} : {e}")

    def create_schema(self, engine, schema_name):
        """Create a schema"""
        try:
            # passé en AUTOCOMMIT pour éviter un probleme de rollback avec SQLAlchemy
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
                inspector = inspect(connection)

                # Vérification de l'existence du schéma avec inspect.has_schema
                if not inspector.has_schema(schema_name):
                    connection.execute(CreateSchema(schema_name, if_not_exists=True))
                    print(f"Création du schéma '{schema_name}' => OK")
                else:
                    print(f"Le schéma '{schema_name}' existe déjà")
        except Exception as e:
            print(f"Erreur lors de la création du schéma '{schema_name}' : {e}")

    def create_tables(self, base, engine, schema_name):
        """Create tables with SQLAlchemy (psycopg2 engine)."""
        try:
            # on regarde si les tables existent déjà
            inspector = inspect(engine)

            # Inspection des tables dans le schéma récupéré
            existing_tables = inspector.get_table_names(schema=schema_name)

            # on compare les tables a ajouter avec celles déjà existantes
            tables_to_create = []
            tables_already_existing = []
            for table in base.metadata.tables.values():
                # dans le cas ou la table qu'on souhaite créée existe déjà on l'ajoute a tables_already_existing
                if table.name in existing_tables:
                    tables_already_existing.append(table.name)
                else:
                    # dans le cas ou la table a créée n'existe pas encore, on l'ajoute a tables_to_create
                    tables_to_create.append(table)
            if tables_already_existing:
                print(f"Ces tables doivent être créés mais existent déjà : {tables_already_existing}")

            # on créé les tables manquantes
            if tables_to_create:
                with engine.begin() as connection:
                    base.metadata.create_all(connection, tables=tables_to_create)

                    print(f"Création des tables : {[table.name for table in tables_to_create]} => OK")
            else:
                print("Toutes les tables existent déjà.")
        except Exception as e:
            print(f"Erreur lors de la création des tables : {e}")


if __name__ == "__main__":
    # Initialisation de la configuration
    db_init = DatabaseInit()

    # Création de la base avec pg8000
    db_init.create_new_db()

    # Création de l'engine pour la nouvelle base avec psycopg2 (pour les schémas et les tables)
    engine = create_engine(db_init.new_psycopg2_url_object, echo=ECHO, future=True)

    # Création du schéma
    db_init.create_schema(engine, schema_name=db_init.DATABASE_SCHEMA)

    # Création des tables
    # note : on n'instancie pas base mais on travaille de manière "globale" (reco SLQAlchemy)
    db_init.create_tables(Base, engine, schema_name=db_init.DATABASE_SCHEMA)

    # creation d'une session pour travailler avec la base
    # Session = sessionmaker(bind=engine, future=True)
    # session = Session()

    # création des comptes de test
    # user_service = UserService(session)
    # user_service.create_test_accounts()