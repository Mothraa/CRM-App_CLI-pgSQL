import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from my_app.config_loader import SENTRY_DSN, DEBUG_MODE
from my_app.cli.main_cli import cli


sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=1.0,
    debug=DEBUG_MODE,
    # pour laisser le temps a sentry d'envoyer les messages a la fermeture
    shutdown_timeout=2,
)

if __name__ == "__main__":

    cli()
