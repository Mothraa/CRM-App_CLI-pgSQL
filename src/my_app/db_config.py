from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from .config_loader import (DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, SSL_MODE,
                            DATABASE_APP_USER, DATABASE_APP_PASSWORD, DEBUG_MODE)


def get_engine(engine=None, database_name=DATABASE_NAME):
    """create and return a SQLAlchemy engine
    param : engine values :  psycopg2 by default, can use pg8000"""
    if not engine or engine == "psycopg2":
        driver_name = "postgresql+psycopg2"
        query_params = {"sslmode": SSL_MODE}
    elif engine == "pg8000":
        driver_name = "postgresql+pg8000"
        query_params = {}

    # note : DATABASE_SCHEMA pas utile ici, la connexion est au niveau de la base
    url_object = URL.create(
        driver_name,
        username=DATABASE_APP_USER,
        password=DATABASE_APP_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=database_name,
        query=query_params,
    )

    return create_engine(url_object, echo=DEBUG_MODE, future=True)


def get_session():
    """Retourne une session SQLAlchemy basée sur l'engine"""
    print("get_session() called with database:", DATABASE_NAME)  # Debug
    engine = get_engine()
    session_local = sessionmaker(bind=engine)
    return session_local()  # on retourne une instance de session
