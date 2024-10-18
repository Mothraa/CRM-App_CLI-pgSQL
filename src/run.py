from my_app.db_config import get_session
from my_app.cli.cli import cli

if __name__ == "__main__":

    # # on récupère une session locale depuis db_config
    # session_local = get_session()

    # # on lance la CLI avec la session locale
    # cli(obj={"session": session_local})

    # on lance la CLI avec un dict vide dans le contexte
    cli(obj={})
