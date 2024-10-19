import click
from my_app.db_config import get_session
from my_app.controllers.main_controller import MainController
from my_app.exceptions import AuthenticationError, LogoutError


# Commande principale Click
@click.group()  # pas de nom pour simplifier la saisie dans le terminal pour les commandes principales
@click.pass_context
def cli(ctx):
    # initialisation de la session
    session = get_session()
    ctx.ensure_object(dict)
    ctx.obj['controller'] = MainController(session)


# Commande d'authentification
@cli.command(help="Authentificate the user with his email and password")
@click.argument('email', metavar='<email utilisateur>', required=True)
@click.pass_context
def login(ctx, email):
    """Authentificate the user"""
    # saisie du mdp masquée
    password = click.prompt("Mot de passe", hide_input=True)

    controller = ctx.obj['controller']
    try:
        controller.authenticate_user_controller(email, password)
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
    controller = ctx.obj['controller']
    try:
        controller.logout()
        # Confirmation de la déconnexion
        click.echo("Déconnexion réussie.")
    except (Exception) as e:
        raise LogoutError(f"Erreur inattendue lors de la déconnexion : {str(e)}")
