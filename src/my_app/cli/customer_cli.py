import click
from rich.console import Console
from my_app.dependencies import init_customer_controller
# from my_app.exceptions import CustomerNotFoundError
from my_app.decorators import requires_auth
from my_app.utils.display_utils import NOT_AVAILABLE_CARACTER, COLUMN_STYLES, create_table


console = Console()


@click.group(help="Customer commands")
@click.pass_context
def customer(ctx):
    """Group of commands to manage customers"""
    session = ctx.obj['session']
    # init de CustomerController et stockage dans le contexte
    ctx.obj['customer_controller'] = init_customer_controller(session)


@customer.command(help="List all customers")
@requires_auth
@click.pass_context
def list(ctx):
    """Display all customers"""
    customer_controller = ctx.obj.get('customer_controller')
    # on récupère l'utilisateur authentifié
    current_user = ctx.obj['authenticated_user']
    customers = customer_controller.list_customers(current_user)

    columns = {
        "ID": COLUMN_STYLES["id"],
        "Company Name": COLUMN_STYLES["name"],
        "Full Name": COLUMN_STYLES["full_name"],
        "Email": COLUMN_STYLES["email"],
        "Phone Number": COLUMN_STYLES["phone_number"],
        "Sales Contact": COLUMN_STYLES["sales_contact"],
        "Created At": COLUMN_STYLES["created_at"]
    }

    table = create_table(columns)

    # ajout des lignes
    for customer in customers:
        if customer.sales_contact:
            sales_contact_first_name = customer.sales_contact.first_name or ""  # pour éviter d'avoir des None
            sales_contact_last_name = customer.sales_contact.last_name or ""
            sales_contact_name = f"{sales_contact_first_name} {sales_contact_last_name}"
        else:
            sales_contact_name = NOT_AVAILABLE_CARACTER

        table.add_row(
            str(customer.id),
            customer.company_name,
            customer.full_name,
            customer.email or NOT_AVAILABLE_CARACTER,
            customer.phone_number or NOT_AVAILABLE_CARACTER,
            sales_contact_name,
            customer.created_at.strftime("%Y-%m-%d %H:%M")
        )
    console.print(table)
