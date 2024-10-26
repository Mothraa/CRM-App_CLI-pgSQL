import click
from my_app.models import RoleType  # Import des rôles définis dans le modèle
from rich.console import Console
from my_app.dependencies import init_user_controller
from my_app.decorators import requires_auth, handle_exceptions
from my_app.utils.display_utils import NOT_AVAILABLE_CARACTER, COLUMN_STYLES, create_table

console = Console()


def display_user_table(users):
    """Display customer details in a table"""
    columns = {
        "ID": COLUMN_STYLES["id"],
        "Email": COLUMN_STYLES["email"],
        "First Name": COLUMN_STYLES["first_name"],
        "Last Name": COLUMN_STYLES["last_name"],
        "Role": COLUMN_STYLES["role"],
        "Created At": COLUMN_STYLES["created_at"]
    }

    table = create_table(columns)

    # ajout des lignes du tableau
    for user in users:
        table.add_row(
            str(user.id),
            user.email,
            user.first_name or NOT_AVAILABLE_CARACTER,
            user.last_name or NOT_AVAILABLE_CARACTER,
            user.role,
            user.created_at.strftime("%Y-%m-%d %H:%M")
        )
    return table


@click.group(help="User commands")
@click.pass_context
def user(ctx):
    """Group of commands to manage users"""
    session = ctx.obj['session']
    # init de UserController et stockage dans le contexte
    ctx.obj['user_controller'] = init_user_controller(session)


@user.command(help="List all users")
@requires_auth
@click.pass_context
@handle_exceptions
def list(ctx):
    """Display all users"""
    user_controller = ctx.obj.get('user_controller')
    # on récupère l'utilisateur authentifié
    current_user = ctx.obj['authenticated_user']
    users = user_controller.list(current_user)

    table = display_user_table(users)
    console.print(table)


@user.command(help="Get a user by ID")
@requires_auth
@click.argument('user_id', type=int, required=True)
@click.pass_context
@handle_exceptions
def get(ctx, user_id):
    """Retrieve and display a single user by his ID"""
    user_controller = ctx.obj.get('user_controller')
    current_user = ctx.obj['authenticated_user']
    user = user_controller.get(current_user, user_id)
    if not user:
        console.print(f"[red]Customer ID {user_id} not found.[/red]")
        return
    table = display_user_table([user])
    console.print(table)


@user.command(help="Add a new user")
@requires_auth
@click.argument('email', metavar='<user email>', required=True)
@click.argument('password', metavar='<user password>', required=True)
@click.argument('role', metavar='<user role>', type=click.Choice([r.value for r in RoleType]), required=True)
@handle_exceptions
@click.pass_context
def add(ctx, email, password, role):
    """Add a new user"""
    current_user = ctx.obj['authenticated_user']
    user_controller = ctx.obj['user_controller']
    user_controller.add(current_user, {'email': email, 'password': password, 'role': role})
    console.print(f"User {email} added!")


@user.command(help="Update a user")
@requires_auth
@click.argument('user_id', metavar='<user id>', required=True)
@click.option('--email', metavar='<new email>', help="change email address")
@click.option('--role', metavar='<new role>',
              type=click.Choice([r.value for r in RoleType]),
              help="change the user role")
@handle_exceptions
@click.pass_context
def update(ctx, user_id, email=None, role=None):
    """Update a user"""
    current_user = ctx.obj['authenticated_user']
    user_controller = ctx.obj['user_controller']
    update_data = {}

    if email:
        update_data['email'] = email
    if role:
        update_data['role'] = role

    if not update_data:
        console.print("No data for update")
        return

    user_controller.update(current_user, user_id, update_data)
    console.print(f"User {email} (ID: {user_id}) updated!")


@user.command(help="Delete a user")
@requires_auth
@click.argument('user_id', metavar='<user id>', required=True)
@handle_exceptions
@click.pass_context
def delete(ctx, user_id):
    """Delete a user"""
    current_user = ctx.obj['authenticated_user']
    user_controller = ctx.obj['user_controller']
    user_controller.delete(current_user, user_id)
    console.print(f"User {user_id} deleted!")
