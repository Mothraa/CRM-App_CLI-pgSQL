import click
from rich.console import Console
from my_app.dependencies import init_event_controller
from my_app.decorators import requires_auth, handle_exceptions
from my_app.utils.display_utils import NOT_AVAILABLE_CARACTER, COLUMN_STYLES, create_table

console = Console()


def display_event_table(events):
    """Display event details in a table"""
    columns = {
        "ID": COLUMN_STYLES["id"],
        "Name": COLUMN_STYLES["event_name"],
        "Location": COLUMN_STYLES["location"],
        "Start Date": COLUMN_STYLES["start_date"],
        "End Date": COLUMN_STYLES["end_date"],
        "Contract": COLUMN_STYLES["contract"],
        "Support Contact": COLUMN_STYLES["support_contact"],
        "Created At": COLUMN_STYLES["created_at"]
    }

    table = create_table(columns)

    # ajout des lignes
    for event in events:
        if event.support_contact:
            support_contact_first_name = event.support_contact.first_name or ""  # pour éviter d'avoir des None
            support_contact_last_name = event.support_contact.last_name or ""
            support_contact_name = f"{support_contact_first_name} {support_contact_last_name}"
        else:
            support_contact_name = NOT_AVAILABLE_CARACTER

        contract_id = str(event.contract.id) if event.contract else NOT_AVAILABLE_CARACTER

        table.add_row(
            str(event.id),
            event.name or NOT_AVAILABLE_CARACTER,
            event.location or NOT_AVAILABLE_CARACTER,
            event.start_date.strftime("%Y-%m-%d %H:%M") if event.start_date else NOT_AVAILABLE_CARACTER,
            event.end_date.strftime("%Y-%m-%d %H:%M") if event.end_date else NOT_AVAILABLE_CARACTER,
            contract_id,
            support_contact_name,
            event.created_at.strftime("%Y-%m-%d %H:%M")
        )
    return table


@click.group(help="Event commands")
@click.pass_context
def event(ctx):
    """Group of commands to manage events"""
    session = ctx.obj['session']
    # init de EventController et stockage dans le contexte
    ctx.obj['event_controller'] = init_event_controller(session)


@event.command(help="List all events")
@requires_auth
@click.option('--no-support', is_flag=True, help="List only events without support contact")
@click.option('--assigned', is_flag=True, help="List only events assigned to the current user (support team)")
@click.pass_context
@handle_exceptions
def list(ctx, no_support, assigned):
    """Display all events"""
    event_controller = ctx.obj.get('event_controller')
    # on récupère l'utilisateur authentifié
    current_user = ctx.obj['authenticated_user']
    events = event_controller.list(user=current_user, filter_no_support=no_support, assigned=assigned)

    table = display_event_table(events)
    console.print(table)


@event.command(help="Get an event by ID")
@requires_auth
@click.argument('event_id', type=int, required=True)
@click.pass_context
@handle_exceptions
def get(ctx, event_id):
    """Retrieve and display an event by ID"""
    event_controller = ctx.obj.get('event_controller')
    current_user = ctx.obj['authenticated_user']
    event = event_controller.get(event_id, current_user)

    if not event:
        console.print(f"[red]event with ID {event_id} not found.[/red]")
        return

    table = display_event_table([event])
    console.print(table)


@event.command(help="Add a event")
@requires_auth
@click.option('--name', metavar="<event name>", help="Name of the event")
@click.option('--location', metavar="<event location>", help="Location of the event")
@click.option('--start_date', metavar="<YYYY-MM-DD HH:MM>", help="Start date format: YYYY-MM-DD HH:MM")
@click.option('--end_date', metavar="<YYYY-MM-DD HH:MM>", help="End date format: YYYY-MM-DD HH:MM")
@click.option('--contract_id', metavar="<signed contract id>", type=int, help="ID of the associated signed contract")
@click.option('--attendees', help="Name of attendees", default=None)
@click.option('--comments', help="Comment field", default=None)
@click.pass_context
@handle_exceptions
def add(ctx, name, location, start_date, end_date, contract_id, attendees, comments):
    """Add an Event"""
    event_controller = ctx.obj.get('event_controller')
    current_user = ctx.obj['authenticated_user']
    event_data = {
        "name": name,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "contract_id": contract_id,
        "attendees": attendees,
        "comments": comments,
    }
    event = event_controller.add(current_user, event_data)
    console.print(f"Event '{event.name}' added!")


@event.command(help="Update an event")
@requires_auth
@click.argument('event_id', metavar="<event id>", type=int, required=True)
@click.option('--name', metavar="<event name>", help="Name of the event")
@click.option('--location', metavar="<event location>", help="Location of the event")
@click.option('--start_date', metavar="<YYYY-MM-DD HH:MM>", help="Start date format: YYYY-MM-DD HH:MM")
@click.option('--end_date', metavar="<YYYY-MM-DD HH:MM>", help="End date format: YYYY-MM-DD HH:MM")
@click.option('--support_id', metavar="<support user id>", type=int, help="ID of the support contact")
@click.option('--attendees', metavar="<attendees names>", help="Name of attendees")
@click.option('--comments', metavar="<comments>", help="Comment field")
@click.pass_context
@handle_exceptions
def update(ctx, event_id, name, location, start_date, end_date, support_id, attendees, comments):
    """Update an event"""
    event_controller = ctx.obj.get('event_controller')
    current_user = ctx.obj['authenticated_user']
    event_data = {k: v for k, v in {
        "name": name,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "contact_support_id": support_id,
        "attendees": attendees,
        "comments": comments,
    }.items() if v is not None}

    event_controller.update(current_user, event_id, event_data)
    console.print(f"Event ID {event_id} updated!")


@event.command(help="Delete an event")
@requires_auth
@click.argument('event_id', type=int, required=True)
@click.pass_context
@handle_exceptions
def delete(ctx, event_id):
    """Delete an event"""
    event_controller = ctx.obj.get('event_controller')
    current_user = ctx.obj['authenticated_user']
    event_controller.delete(current_user, event_id)
    console.print(f"Event ID {event_id} deleted!")
