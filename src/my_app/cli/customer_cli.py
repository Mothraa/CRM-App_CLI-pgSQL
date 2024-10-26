import click
from rich.console import Console
from my_app.dependencies import init_customer_controller
from my_app.decorators import requires_auth, handle_exceptions
from my_app.utils.display_utils import NOT_AVAILABLE_CARACTER, COLUMN_STYLES, create_table


console = Console()


def display_customer_table(customers):
    """Display customer details in a table format"""
    columns = {
        "ID": COLUMN_STYLES["id"],
        "Company Name": COLUMN_STYLES["company name"],
        "Full Name": COLUMN_STYLES["full_name"],
        "Email": COLUMN_STYLES["email"],
        "Phone Number": COLUMN_STYLES["phone_number"],
        "Sales Contact": COLUMN_STYLES["sales_contact"],
        "Created At": COLUMN_STYLES["created_at"]
    }
    table = create_table(columns)

    for customer in customers:
        sales_contact_name = NOT_AVAILABLE_CARACTER
        if customer.sales_contact:
            sales_contact_first_name = customer.sales_contact.first_name or ""
            sales_contact_last_name = customer.sales_contact.last_name or ""
            sales_contact_name = f"{sales_contact_first_name} {sales_contact_last_name}"

        table.add_row(
            str(customer.id),
            customer.company_name,
            customer.full_name,
            customer.email or NOT_AVAILABLE_CARACTER,
            customer.phone_number or NOT_AVAILABLE_CARACTER,
            sales_contact_name,
            customer.created_at.strftime("%Y-%m-%d %H:%M")
        )
    return table


@click.group(help="Customer commands")
@click.pass_context
def customer(ctx):
    """Group of commands to manage customers"""
    session = ctx.obj["session"]
    # init de CustomerController et stockage dans le contexte
    ctx.obj["customer_controller"] = init_customer_controller(session)


@customer.command(help="List all customers")
@requires_auth
@click.pass_context
@handle_exceptions
def list(ctx):
    """Display all customers"""
    customer_controller = ctx.obj.get("customer_controller")
    current_user = ctx.obj["authenticated_user"]
    customers = customer_controller.list(current_user)

    if not customers:
        console.print("No customers found")
        return

    table = display_customer_table(customers)
    console.print(table)


@customer.command(help="Get a customer by ID")
@requires_auth
@click.argument("customer_id", type=int, required=True)
@click.pass_context
@handle_exceptions
def get(ctx, customer_id):
    """Retrieve and display a customer by his ID"""
    customer_controller = ctx.obj.get("customer_controller")
    current_user = ctx.obj["authenticated_user"]
    customer = customer_controller.get(customer_id, current_user)

    if not customer:
        console.print(f"[red]Customer ID {customer_id} not found.[/red]")
        return

    table = display_customer_table([customer])  # Liste contenant un seul client
    console.print(table)


@customer.command(help="Add a new customer")
@requires_auth
@click.argument("company_name", metavar="<company name>", required=True)
@click.argument("full_name", metavar="<full name>", required=True)
@click.option("--email", metavar="<email>", required=False, help="customer email address")
@click.option("--phone", metavar="<phone number>", required=False, help="customer phone number")
@click.pass_context
@handle_exceptions
def add(ctx, company_name, full_name, email, phone):
    """Add a new customer"""
    current_user = ctx.obj["authenticated_user"]
    customer_controller = ctx.obj["customer_controller"]

    customer_data = {
        "company_name": company_name,
        "full_name": full_name,
        "email": email,
        "phone_number": phone,
    }

    customer_controller.add(current_user, customer_data)
    console.print("Customer added!")


@customer.command(help="Update an existing customer")
@requires_auth
@click.argument("customer_id", metavar="<customer id>", type=int, required=True)
@click.option("--company_name", metavar="<company name>", required=False, help="company name")
@click.option("--full_name", metavar="<full name>", required=False, help="customer full name")
@click.option("--email", metavar="<email>", required=False, help="customer email address")
@click.option("--phone", metavar="<phone number>", required=False, help="customer phone number")
@click.option("--sales_id", metavar="<sales contact ID>",
              type=int, required=False, help="ID of the sales contact")
@click.pass_context
@handle_exceptions
def update(ctx, customer_id, company_name, full_name, email, phone, sales_id):
    """Update an existing customer"""
    current_user = ctx.obj["authenticated_user"]
    customer_controller = ctx.obj["customer_controller"]

    # on ajoute les données au dictionnaire
    update_data = {
        key: value for key, value in {
            "company_name": company_name,
            "full_name": full_name,
            "email": email,
            "phone_number": phone,
            "contact_sales_id": sales_id
        }.items() if value is not None
    }

    if not update_data:
        console.print("No data to update!")
        return

    customer_controller.update(customer_id, update_data, current_user)
    console.print(f"Customer {customer_id} updated!")


@customer.command(help="Delete a customer")
@requires_auth
@click.argument("customer_id", metavar="<customer id>", required=True)
@click.pass_context
@handle_exceptions
def delete(ctx, customer_id):
    """Delete a customer"""
    current_user = ctx.obj["authenticated_user"]
    customer_controller = ctx.obj["customer_controller"]
    customer_controller.delete(current_user, customer_id)
    console.print(f"Customer {customer_id} deleted!")
