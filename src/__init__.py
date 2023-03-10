from flask import Flask

from src.models import db
from src.routes import frames_bp, saved_frames_bp, videos_bp


def create_flask_app(config: dict) -> Flask:
    """Функция для создания Flask приложения.
    
    Args:
        config: Конфигурация Flask приложения.

    Returns:
        Flask приложение.
    """
    app = Flask(__name__)
    app.config.from_mapping(config)

    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(frames_bp, url_prefix='/api/frames')
    app.register_blueprint(saved_frames_bp, url_prefix='/api/saved_frames')

    db.init_app(app)
    return app
