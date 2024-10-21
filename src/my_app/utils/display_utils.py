from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# init de rich
# autre possibilité, surcharger print : from rich import print
console = Console()

NOT_AVAILABLE_CARACTER = "--"

COLUMN_STYLES = {
    "id": "sky_blue1",
    "name": "green",
    "full_name": "orange3",
    "email": "deep_pink4",
    "phone_number": "yellow3",
    "sales_contact": "bold cyan",
    "created_at": "grey74"
}


def display_authenticated_user(authenticated_user):
    """Display the authentificated user on a Panel in top right corner"""
    if authenticated_user:
        # Remplacer None par une chaîne vide ("") pour les champs manquants
        first_name = authenticated_user.first_name or ""
        last_name = authenticated_user.last_name or ""
        email = authenticated_user.email or ""

        first_name_fixed = first_name[:20]  # 20 caractères max a l'affichage (tronqué)
        last_name_fixed = last_name[:20]
        email_fixed = email[:50]

        user_info = (
            f"Identified as: [bold cyan]{first_name_fixed} {last_name_fixed}[/bold cyan] "
            f"([deep_pink4]{email_fixed}[/deep_pink4])"
        )
        panel = Panel(user_info, title="App User Infos", width=100, expand=False)
        console.print(panel, justify="left")
    else:
        console.print(Panel("[red]No user authenticated[/red]", title="User Info", expand=False), justify="left")


def create_table(columns):
    """Crée une table avec des colonnes et des styles prédéfinis"""
    table = Table()
    for col, style in columns.items():
        table.add_column(col, style=style, no_wrap=True)
    return table
