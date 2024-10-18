from getpass import getpass

import click

from my_app.db_config import get_session
from my_app.controllers.main_controller import MainController


@click.group()
@click.pass_context
def cli(ctx):
    """Entry point for the CLI"""
    # si l'utilisateur n'est pas authentifié, on le force a se connecter
    if ctx.obj is None or not ctx.obj.get("authenticated_user"):
        click.echo("You must login before using the app!")
        ctx.invoke(login)

    # si l'utilisateur est authentifié...
    if ctx.obj.get("authenticated_user"):
        if "controller" not in ctx.obj:
            # on initialise le controleur
            ctx.obj["controller"] = MainController(ctx.obj["session"])


@click.command()
@click.pass_context
def login(ctx):
    """Command to log in a user and create session"""

    # Demander les identifiants via le prompt
    email = click.prompt("Email : ")
    password = getpass("Password : ")

    # Créer une session SQLAlchemy après authentification réussie
    session = get_session()

    # Initialiser le contrôleur pour l'authentification
    controller = MainController(session)

    try:
        # Authentifier l'utilisateur via le contrôleur
        user = controller.authenticate_user_controller(email, password)

        # Stocker le contrôleur et la session dans le contexte CLI
        ctx.ensure_object(dict)
        ctx.obj["authenticated_user"] = user
        ctx.obj["session"] = session
        ctx.obj["controller"] = controller
        # L'utilisateur authentifié est stocké dans le context mais aussi dans le 
        # controleur. On peut y faire appel avec controller.get_authenticated_user
        # (TODO : a revoir ? pourrait poser des pb de données dupliquées ; permet de maintenir la session)

        click.echo(f"Bienvenue {controller.get_authenticated_user().first_name} !")

    except Exception as e:
        # Capturer toute exception levée durant le processus d'authentification
        click.echo(f"Erreur lors de l'authentification : {e}")
        ctx.exit(1)


@click.command()
@click.pass_context
def logout(ctx):
    """Command to log out a user"""
    if ctx.obj.get("authenticated_user"):
        # message de deco
        click.echo(f"Ciao {ctx.obj['authenticated_user'].first_name}!")

        # on ferme la session SQLAlchemy avant de la suppr (+ propre)
        if ctx.obj.get("session"):
            ctx.obj["session"].close()

        # on supprime les infos liées a l'auth
        ctx.obj["authenticated_user"] = None
        ctx.obj["session"] = None
        ctx.obj["controller"] = None

        # Confirmation de la déconnexion
        click.echo("Déconnexion => OK")
    else:
        click.echo("Pas d'utilisateur connecté")


# Enregistrer les commandes
cli.add_command(login)
cli.add_command(logout)
