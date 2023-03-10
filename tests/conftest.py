import os
import shutil
from typing import TYPE_CHECKING

import pytest

from src import create_flask_app
from src.utils.config import Config
from src.models import db as test_db
from src.models import FrameServiceInformation

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient
    from flask_sqlalchemy import SQLAlchemy


@pytest.fixture(scope="session")
def app() -> 'Flask':
    """Функция для создания Flask приложения.

    Returns:
        Flask приложение.
    """
    config = Config()
    config.flask['SQLALCHEMY_DATABASE_URI'] = (
        config.flask['SQLALCHEMY_TEST_DATABASE_URI'])
    config.flask['TESTING'] = True
    app = create_flask_app(config.flask)
    return app


@pytest.fixture(scope="function")
def db(app: 'Flask') -> 'SQLAlchemy':
    """Функция для очистки базы данных.

    Args:
        app: Flask приложение.

    Returns:
        База данных с таблицами и без данных.
    """
    with app.app_context():
        test_db.drop_all()
        test_db.create_all()
    return test_db


@pytest.fixture(scope="function")
def client(app: 'Flask') -> 'FlaskClient':
    """Функция для создания тестового клиента.

    Args:
        app: Flask приложение.

    Returns:
        Тестовый клиент.
    """
    return app.test_client()


@pytest.fixture(scope="function")
def clean_frames_dir() -> None:
    """Функция для удаления всех файлов и каталогов из указанного
    в конфигурационном файле каталога с сохранёнными фреймами.
    """
    config = Config()
    frames_dir_path = config.flask['FRAMES_DIR_PATH']
    for dir_name in os.listdir(frames_dir_path):
        dir_path = os.path.join(frames_dir_path, dir_name)
        shutil.rmtree(dir_path)


def create_frame_service_information(
        app: 'Flask',
        db: 'SQLAlchemy',
        video_file_name: str,
        frame_number: int,
        frame_file_path: str,
) -> None:
    """Функция для добавления в базу данных строки со служебной информацией о
    вырезанном кадре.

    Args:
        app: Flask приложение.
        db: Экземпляр класса для работы с базой данных.
        video_file_name: Имя исходного видеофайла.
        frame_number: Порядковый номер вырезанного кадра от начала файла.
        frame_file_path: Полный путь к файлу с вырезанный кадром.
    """
    with app.app_context():
        frame_service_information = FrameServiceInformation(
            video_file_name,
            frame_number,
            frame_file_path
        )
        db.session.add(frame_service_information)
        db.session.commit()
