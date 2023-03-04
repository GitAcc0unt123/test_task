from src.utils.config import Config
from src.models import db
from src import create_flask_app


if __name__ == '__main__':
    config = Config('config.yaml')
    app = create_flask_app(config.flask)

    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
