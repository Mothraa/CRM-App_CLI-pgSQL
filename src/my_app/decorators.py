from functools import wraps

import click
from sentry_sdk import capture_exception, flush, capture_message
from sqlalchemy.exc import SQLAlchemyError


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


# cli
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


def handle_exceptions(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            # on capture l'exception avec sentry
            # TODO : a voir si on exclus de sentry les erreurs de permission (CustomPermissionError)
            capture_exception(e)
            # on force l'envoi immédiat à Sentry (lié a la fermeture rapide de l'app)
            flush()
            click.echo(f"Erreur : {str(e)}")
    return decorated_function


def serialize_args(arg):
    """To manage unserializable data for sentry log"""
    if isinstance(arg, (str, int, float, bool, type(None))):
        return arg
    elif hasattr(arg, "__dict__"):  # For objects with attributes
        return {k: v for k, v in vars(arg).items() if isinstance(v, (str, int, float, bool, type(None)))}
    else:
        return str(arg)


def log_user_actions(action):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            serialized_args = {f"arg_{i}": serialize_args(arg) for i, arg in enumerate(args)}
            serialized_kwargs = {k: serialize_args(v) for k, v in kwargs.items()}
            result = function(*args, **kwargs)
            serialized_result = serialize_args(result)

            # pas besoin de récupérer des infos utilisateurs, fait par sentry via set_user
            capture_message(
                f"Action utilisateur : {action}",
                level="info",
                contexts={
                    "Fonction": {"name": function.__name__},
                    "Args": serialized_args,
                    "Params": serialized_kwargs,
                    "Result": serialized_result,
                }
            )
            flush()
            return result
        return wrapper
    return decorator
