import click
from rich.console import Console

from my_app.dependencies import init_contract_controller
from my_app.decorators import requires_auth, handle_exceptions
from my_app.utils.display_utils import NOT_AVAILABLE_CARACTER, COLUMN_STYLES, CONTRACT_STATUS_ALIASES, create_table
from my_app.models import ContractStatus

console = Console()


def display_contract_table(contracts):
    """Display customer details in a table format"""
    columns = {
        "ID": COLUMN_STYLES["id"],
        "Customer": COLUMN_STYLES["customer_name"],
        "Total Amount": COLUMN_STYLES["total_amount"],
        "Remaining Amount": COLUMN_STYLES["remaining_amount"],
        "Status": COLUMN_STYLES["status"],
        "Sales Contact": COLUMN_STYLES["sales_contact"],
        "Created At": COLUMN_STYLES["created_at"]
    }
    table = create_table(columns)

    table.columns[2].justify = "right"  # Total Amount
    table.columns[3].justify = "right"  # Remaining Amount

    # ajout des lignes
    for contract in contracts:
        if contract.sales_contact:
            sales_contact_first_name = contract.sales_contact.first_name or ""  # pour éviter d"avoir des None
            sales_contact_last_name = contract.sales_contact.last_name or ""
            sales_contact_name = f"{sales_contact_first_name} {sales_contact_last_name}"
        else:
            sales_contact_name = NOT_AVAILABLE_CARACTER

        customer_name = (f"{contract.customer.company_name} ({contract.customer.full_name})"
                         if contract.customer else NOT_AVAILABLE_CARACTER)

        total_amount = f"{contract.total_amount} €" if contract.total_amount else NOT_AVAILABLE_CARACTER
        remaining_amount = f"{contract.remaining_amount} €" if contract.remaining_amount else NOT_AVAILABLE_CARACTER

        contract_status_alias = CONTRACT_STATUS_ALIASES.get(contract.status, contract.status)

        table.add_row(
            str(contract.id),
            customer_name,
            total_amount,
            remaining_amount,
            contract_status_alias,
            sales_contact_name,
            contract.created_at.strftime("%Y-%m-%d %H:%M")
        )
    return table


@click.group(help="Contract commands")
@click.pass_context
def contract(ctx):
    """Group of commands to manage contracts"""
    session = ctx.obj["session"]
    # init de ContractController et stockage dans le contexte
    ctx.obj["contract_controller"] = init_contract_controller(session)


@contract.command(help="List all contracts")
@requires_auth
@click.option('--unsigned', is_flag=True, help="List unsigned contracts")
@click.option('--notpaid', is_flag=True, help="List contracts that are not totally paid")
@click.pass_context
@handle_exceptions
def list(ctx, unsigned, notpaid):
    """Display all contracts"""
    contract_controller = ctx.obj.get("contract_controller")
    # on récupère l"utilisateur authentifié
    current_user = ctx.obj["authenticated_user"]
    contracts = contract_controller.list(user=current_user, unsigned=unsigned, notpaid=notpaid)
    table = display_contract_table(contracts)
    console.print(table)


@contract.command(help="Get a contract by ID")
@requires_auth
@click.argument("contract_id", type=int, required=True)
@click.pass_context
@handle_exceptions
def get(ctx, contract_id):
    """Retrieve and display a contract by his ID"""
    contract_controller = ctx.obj.get("contract_controller")
    current_user = ctx.obj["authenticated_user"]
    contract = contract_controller.get(current_user, contract_id)

    if not contract:
        console.print(f"[red]Customer ID {contract_id} not found.[/red]")
        return

    table = display_contract_table([contract])
    console.print(table)


@contract.command(help="Add a new contract")
@requires_auth
@click.argument("customer_id", metavar="<customer id>", type=int, required=True)
@click.argument("sales_id", metavar="<sales contact id>", type=int, required=True)
@click.option("--total_amount", metavar="<total contract amount>", type=float, help="Total amount of the contract")
@click.option("--status", type=click.Choice([status.value for status in ContractStatus]),
              help="Contract status", required=False)
@click.pass_context
@handle_exceptions
def add(ctx, customer_id, sales_id, total_amount, remaining_amount, status):
    """Add a new contract"""
    current_user = ctx.obj["authenticated_user"]
    contract_controller = ctx.obj["contract_controller"]
    contract_data = {
        "customer_id": customer_id,
        "contact_sales_id": sales_id,
        "total_amount": total_amount,
        "status": status
    }

    contract_controller.add(current_user, contract_data)
    console.print("Contract added!")


@contract.command(help="Update a contract")
@requires_auth
@click.argument('contract_id', metavar="<contract id>", type=int, required=True)
@click.option('--customer_id', metavar="<customer id>", type=int, help="The customer associated with the contract")
@click.option('--sales_id', metavar="<sales contact id>", type=int, help="The sales contact for the contract")
@click.option('--total_amount', metavar="<total contract amount>", type=float, help="Total amount of the contract")
@click.option('--remaining_amount', metavar="<remaining amount to pay>", type=float,
              help="Remaining amount of the contract")
@click.option('--status', type=click.Choice([status.value for status in ContractStatus]), help="Contract status")
@click.pass_context
@handle_exceptions
def update(ctx, contract_id, customer_id, sales_id, total_amount, remaining_amount, status):
    """Update an existing contract"""
    current_user = ctx.obj["authenticated_user"]
    contract_controller = ctx.obj["contract_controller"]

    # ajoute les options choisies au dict
    update_data = {
        key: value for key, value in {
            "customer_id": customer_id,
            "contact_sales_id": sales_id,
            "total_amount": total_amount,
            "remaining_amount": remaining_amount,
            "status": status
        }.items() if value is not None
    }

    if not update_data:
        console.print("[red]No data provided for update![/red]")
        return

    contract_controller.update(current_user, contract_id, update_data)
    console.print(f"Contract {contract_id} updated!")


# pas de delete possible, tous les contrats restent visibles (statut annulé possible)
# @contract.command(help="Delete a contract")
# @requires_auth
# @click.argument("contract_id", metavar="<contract id>", required=True)
# @click.pass_context
# @handle_exceptions
# def delete(ctx, contract_id):
#     """Delete a contract"""
#     current_user = ctx.obj["authenticated_user"]
#     contract_controller = ctx.obj["contract_controller"]
#     contract_controller.delete(current_user, contract_id)
#     console.print(f"Contract {contract_id} deleted!")
