import pytest
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from my_app.db_config import get_session
from my_app.models import RoleType


@pytest.fixture(scope="module")
def session():
    """Fixture who return a SQLAlchemy session"""
    session = get_session()
    yield session
    session.close()  # on oublie pas de fermer la session apres le test...


@pytest.mark.unit
def test_database_connection(session):
    """Check if the database connection is OK"""
    try:
        session.execute(text("SELECT 1"))
    except OperationalError:
        pytest.fail("La connexion à la base de données a échoué.")


@pytest.mark.unit
def test_select_privilege(session):
    """Check if the user can use SELECT on tables"""
    try:
        result = session.execute(text("SELECT * FROM crm.\"user\" LIMIT 1"))
        assert result is not None, "L'utilisateur ne peut pas faire de SELECT."
    except OperationalError as e:
        pytest.fail(f"Erreur lors de l'exécution du SELECT: {e}")


@pytest.mark.unit
def test_insert_privilege(session):
    """Check if the user can INSERT data on tables"""
    try:
        now = datetime.now()
        session.execute(text(f"INSERT INTO crm.\"user\" (email, password_hash, role, created_at) \
                             VALUES ('test@test.com', 'test_hash', '{RoleType.admin.value}', :created_at)"),
                        {'created_at': now})
        session.commit()
    except OperationalError as e:
        pytest.fail(f"L'utilisateur ne peut pas insérer des données: {e}")
    finally:
        # on nettoye les données précédemment créées après le test
        session.execute(text("DELETE FROM crm.\"user\" WHERE email = 'test@test.com'"))
        session.commit()


@pytest.mark.unit
def test_update_privilege(session):
    """Check if the user can UPDATE data on tables"""
    try:
        # on ajoute dans un premier temps une entité
        now = datetime.now()
        session.execute(text(f"INSERT INTO crm.\"user\" (email, password_hash, role, created_at) \
                             VALUES ('test@test.com', 'test_hash', '{RoleType.admin.value}', :created_at)"),
                        {'created_at': now})
        session.commit()

        # test d'UPDATE
        session.execute(text("UPDATE crm.\"user\" SET password_hash = 'new_hash' WHERE email = 'test@test.com'"))
        session.commit()

        result = session.execute(text("SELECT password_hash FROM crm.\"user\" WHERE email = 'test@test.com'"))
        assert result.fetchone()[0] == 'new_hash', "L'utilisateur ne peut pas mettre à jour des données."
    except OperationalError as e:
        pytest.fail(f"L'utilisateur ne peut pas mettre à jour des données: {e}")
    finally:
        # on nettoye les données précédemment créées après le test
        session.execute(text("DELETE FROM crm.\"user\" WHERE email = 'test@test.com'"))
        session.commit()


@pytest.mark.unit
def test_delete_privilege(session):
    """Check if the user can DELETE data on tables"""
    try:
        # on ajoute dans un premier temps une entité
        now = datetime.now()
        session.execute(text(f"INSERT INTO crm.\"user\" (email, password_hash, role, created_at) \
                             VALUES ('test@test.com', 'test_hash', '{RoleType.admin.value}', :created_at)"),
                        {'created_at': now})
        session.commit()

        # Test delete
        session.execute(text("DELETE FROM crm.\"user\" WHERE email = 'test@test.com'"))
        session.commit()

        result = session.execute(text("SELECT * FROM crm.\"user\" WHERE email = 'test@test.com'"))
        assert result.fetchone() is None, "L'utilisateur ne peut pas supprimer des données."
    except OperationalError as e:
        pytest.fail(f"L'utilisateur ne peut pas supprimer des données: {e}")
