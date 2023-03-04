from src.utils.config import Config
from src import create_flask_app

config = Config('config.yaml')
application = create_flask_app(config.flask)

if __name__ == '__main__':
    application.run()