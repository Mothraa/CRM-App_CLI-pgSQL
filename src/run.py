from client import Client

from my_app.config_loader import TIME_ZONE

if __name__ == "__main__":
    client = Client()
    client.run()
