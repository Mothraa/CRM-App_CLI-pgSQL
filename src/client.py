# from my_app.controllers.main_controller import MainController
from my_app.cli.commands import cli


class Client:
    def __init__(self):
        pass
        # self.app = MainController()

    def run(self):
        cli()
        # self.app.run()
