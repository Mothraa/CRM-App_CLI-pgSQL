import click
from rich.traceback import install

from my_app.db_config import get_session
from my_app.exceptions import AuthenticationError, LogoutError
from my_app.dependencies import init_main_controller
from my_app.cli.customer_cli import customer
from my_app.utils.display_utils import display_authenticated_user

install()  # activation des exceptions via rich


# Commande principale Click
@click.group()  # pas de nom pour simplifier la saisie dans le terminal pour les commandes principales
@click.pass_context
def cli(ctx):
    # initialisation de la session
    session = get_session()
    # ctx.obj['controller'] = session
    ctx.ensure_object(dict)
    ctx.obj["session"] = session
    ctx.obj["main_controller"] = init_main_controller(session)

    # on récupère l'utilisateur authentifié à partir des tokens si disponibles
    controller = ctx.obj['main_controller']
    authenticated_user = controller.verify_and_refresh_token()

    # on le stock dans le contexte
    if authenticated_user:
        ctx.obj['authenticated_user'] = authenticated_user
    else:
        ctx.obj['authenticated_user'] = None

    # fonction d'affichage de l'utilisateur authentifié
    if ctx.invoked_subcommand not in ["login", "logout"]:  # on exclus l'affichage pour login et logout
        display_authenticated_user(authenticated_user)


# Commande d'authentification
@cli.command(help="Authentificate the user with his email and password")
@click.argument('email', metavar='<user email>', required=True)
@click.pass_context
def login(ctx, email):
    """Authentificate the user"""
    # saisie du mdp masquée
    password = click.prompt("Mot de passe", hide_input=True)
    controller = ctx.obj['main_controller']
    try:
        user = controller.authenticate_user_controller(email, password)
        if not user:
            click.echo("Mot de passe incorrect.")
            return
        ctx.obj['authenticated_user'] = user  # pas utile actuellement car rechargé a chaque ctx
        click.echo(f"Utilisateur {email} authentifié.")
    # pour récupérer les AuthenticationError de authenticate_user_controller + indeterminées
    except (AuthenticationError, Exception) as e:
        raise AuthenticationError(f"Erreur d'authentification : {str(e)}")


# Commande pour se déconnecter
@cli.command(help="Logout the authentificated user")
@click.pass_context
def logout(ctx):
    """Déconnecte l'utilisateur"""
    # on récupère le controleur pour appeler la methode logout
    controller = ctx.obj['main_controller']
    try:
        if controller.logout():
            ctx.obj['authenticated_user'] = None
            click.echo("Déconnexion réussie.")
        else:
            click.echo("Aucune connexion active.")
    except (Exception) as e:
        raise LogoutError(f"Erreur inattendue lors de la déconnexion : {str(e)}")


# on ajoute le groupe de commandes customer
cli.add_command(customer)
