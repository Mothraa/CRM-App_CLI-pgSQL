# main_cli.py : authentification (login/logout) + filtrage des commandes en fonction des autorisations

import click
from rich.traceback import install

from my_app.db_config import get_session
from my_app.exceptions import LogoutError
from my_app.dependencies import init_main_controller
from my_app.cli.customer_cli import customer
from my_app.cli.contract_cli import contract
from my_app.cli.event_cli import event
from my_app.cli.user_cli import user
from my_app.permissions import filter_commands_by_permissions
from my_app.utils.display_utils import display_authenticated_user
from my_app.decorators import handle_exceptions


install()  # activation des exceptions via rich


def load_controller_and_user(ctx):
    """Initialise la session, le contrôleur principal et authentifie l'utilisateur"""
    session = get_session()
    ctx.ensure_object(dict)  # Assure que le contexte est un dictionnaire
    ctx.obj["session"] = session
    ctx.obj["main_controller"] = init_main_controller(session)

    # Authentification de l'utilisateur via le main_controller
    controller = ctx.obj['main_controller']
    authenticated_user = controller.verify_and_refresh_token()

    # Stocker l'utilisateur authentifié dans le contexte
    if authenticated_user:
        ctx.obj['authenticated_user'] = authenticated_user
    else:
        ctx.obj['authenticated_user'] = None


class HelpFilterGroup(click.Group):
    def get_help(self, ctx):
        """Click help method overload to show only filtered commands"""
        # charge le contrôleur et l'utilisateur
        load_controller_and_user(ctx)

        filter_commands_by_permissions(ctx)
        return super().get_help(ctx)


@click.group(cls=HelpFilterGroup, invoke_without_command=True)
@click.pass_context
@handle_exceptions
def cli(ctx):
    """Click main command"""
    # charge le contrôleur et l'utilisateur
    load_controller_and_user(ctx)

    # si aucune sous command invoquée, on affiche l'aide (--help)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

    # fonction d'affichage de l'utilisateur authentifié
    # Exclusion des cas de `--help` (racine) ou pour `login/logout`
    if (
        ctx.invoked_subcommand not in ["login", "logout"] and
        ctx.invoked_subcommand is not None
    ):
        display_authenticated_user(ctx.obj['authenticated_user'])


@cli.command(help="Authentificate the user")
@click.argument('email', metavar='<user email>', required=True)
@click.pass_context
@handle_exceptions
def login(ctx, email):
    """Command for authentificate the user"""
    # saisie du mdp masquée
    password = click.prompt("Mot de passe", hide_input=True)
    controller = ctx.obj['main_controller']

    user = controller.authenticate_user_controller(email, password)
    if not user:
        click.echo("Mot de passe incorrect.")
        return
    ctx.obj['authenticated_user'] = user  # pas utile actuellement car rechargé a chaque ctx
    click.echo(f"Utilisateur {email} authentifié.")


# Commande pour se déconnecter
@cli.command(help="Logout the authentificated user")
@click.pass_context
@handle_exceptions
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


# on ajoute les groupes de commandes spécifiques a chaque table
cli.add_command(user)
cli.add_command(customer)
cli.add_command(contract)
cli.add_command(event)
