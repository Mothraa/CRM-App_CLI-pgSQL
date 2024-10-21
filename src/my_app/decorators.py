from functools import wraps

from sqlalchemy.exc import SQLAlchemyError
import click


# base_repository
def exec_transaction(func):
    """Decorator to handle database transactions"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
            self.db_session.commit()
            return result
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise Exception(f"Transaction failed: {e}")
        # pour les exceptions non liées aux transactions (pour qu'elles ne soient pas masquées)
        except Exception:
            # on fait quand même un rollback
            self.db_session.rollback()
            raise  # relance l'exception d'origine (par exemple "ID not found")
    return wrapper


# *_cli
def requires_auth(f):
    @click.pass_context
    @wraps(f)
    def decorated_function(ctx, *args, **kwargs):
        ctx.ensure_object(dict)
        if ctx.obj.get('authenticated_user') is None:
            click.echo("Vous devez être connecté.")
            return
        return ctx.invoke(f, *args, **kwargs)
    return decorated_function
