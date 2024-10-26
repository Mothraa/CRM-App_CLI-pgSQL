from my_app.models import User
from my_app.exceptions import CustomPermissionError

# permissions sous forme de dict, alternative plus évoluée => casbin

ROLES_PERMISSIONS = {
    "admin": [
        "view-user", "add-user", "update-user", "delete-user",
        "view-customer", "add-customer", "update-customer", "delete-customer",
        "view-contract", "add-contract", "update-contract", "delete-contract",
        "view-event", "add-event", "update-event", "delete-event",
    ],
    "manage": [
        "view-user", "add-user", "update-user", "delete-user",
        "view-contract", "add-contract", "update-contract",
        "view-event", "update-event", "delete-event",
        "filter-event-without-support"
    ],
    "sales": [
        "view-user",
        "view-customer", "add-customer", "update-customer",
        "view-contract", "update-contract", "filter-contracts-assigned",
        "view-event", "add-event",  # add event sans pouvoir assigner l'user support
    ],
    "support": [
        "view-user",
        "view-customer",
        "view-contract",
        "view-event", "update-event", "filter-events-assigned"
    ],
}

COMMANDS_PERMISSIONS = {
    'customer': {
        'list': 'view-customer',
        'add': 'add-customer',
        'update': 'update-customer',
        'delete': 'delete-customer'
    },
    'contract': {
        'list': 'view-contract',
        'add': 'add-contract',
        'update': 'update-contract',
        'delete': 'delete-contract'
    },
    'event': {
        'list': 'view-event',
        'add': 'add-event',
        'update': 'update-event',
        'delete': 'delete-event'
    },
    'user': {
        'list': 'view-user',
        'add': 'add-user',
        'update': 'update-user',
        'delete': 'delete-user'
    }
}


def check_permission(authenticated_user: User, required_permission: str):
    """Check if the authenticated user has the required permission."""
    if authenticated_user is None:
        raise CustomPermissionError("User is not authenticated.")

    if required_permission not in ROLES_PERMISSIONS.get(authenticated_user.role, []):
        raise CustomPermissionError(f"You don't have permission: {required_permission}")
    return True


# pour le filtrage de l'aide de click
def filter_commands_by_permissions(ctx):
    """fonction qui affiche les commandes en fonction des permissions"""
    # on récupère l'utilisateur authentifié
    authenticated_user = ctx.obj.get("authenticated_user")

    # Si aucun utilisateur n'est authentifié
    if not authenticated_user:
        # Si on est dans le cas de `--help`, ne pas filtrer les commandes
        if ctx.invoked_subcommand == "help":
            print("DEBUG: Aucune authentification pour --help, ne rien filtrer.")
            return  # Pas de filtrage des commandes

        # Si on n'est pas dans le cas de `help`, masquer les groupes de commandes
        print("DEBUG: Aucun utilisateur authentifié, masquage des commandes !!")
        for group_name in COMMANDS_PERMISSIONS.keys():
            _hide_command_group(ctx, group_name)
        return

    # Si l'utilisateur est authentifié, on applique le filtrage des commandes
    role = authenticated_user.role
    permissions = ROLES_PERMISSIONS.get(role, [])
    print(f"DEBUG: Permissions pour le rôle {role} : {permissions}")

    # Parcours des commandes et masquage de celles sans permission
    for cli_group_name, command_permissions in COMMANDS_PERMISSIONS.items():
        cli_group = ctx.command.get_command(ctx, cli_group_name)
        if not cli_group:
            continue
        _hide_commands_without_permissions(cli_group, command_permissions, permissions, ctx)


def _hide_command_group(ctx, group_name):
    """Masque un groupe entier de commandes s'il est présent"""
    cli_group = ctx.command.get_command(ctx, group_name)
    if cli_group:
        cli_group.hidden = True
        print(f"DEBUG Groupe '{group_name}' masqué.")


def _hide_commands_without_permissions(cli_group, command_permissions, permissions, ctx):
    """Masque les commandes auxquelles l'utilisateur n'a pas accès"""
    for command_name, required_permission in command_permissions.items():
        command = cli_group.get_command(ctx, command_name)
        if command and required_permission not in permissions:
            command.hidden = True
        #     print(f"DEBUG Commande '{command_name}' masqué, permission requise : '{required_permission}'")
        # else:
        #     print(f"DEBUG Commande '{command_name}' affiché, permission : '{required_permission}'")
