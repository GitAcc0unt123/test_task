import os
from typing import TYPE_CHECKING

from sqlalchemy import select

from tests.conftest import create_frame_service_information
from src.models import FrameServiceInformation
from src.utils.config import Config

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient
    from flask_sqlalchemy import SQLAlchemy


def test_route_saved_frames_get_empty_list(client: 'FlaskClient', db: 'SQLAlchemy'):
    """Функция для тестирования получаемого от сервера списка сохранённых кадров со служебной информацией.

    Args:
        client: Тестовый клиент.
        db: Вызов фикстуры для очистки базы данных перед выполнением теста.
    """
    response = client.get('/api/saved_frames')
    assert response.status_code == 200
    assert response.get_json() == []

    # check idempotent
    response = client.get('/api/saved_frames')
    assert response.status_code == 200
    assert response.get_json() == []


def test_route_saved_frames_get(client: 'FlaskClient', app: 'Flask', db: 'SQLAlchemy'):
    """Функция для тестирования получаемого от сервера списка сохранённых кадров со служебной информацией.

    Args:
        client: Тестовый клиент.
        app: Flask приложение.
        db: Вызов фикстуры для очистки базы данных перед выполнением теста.
    """
    frame_service_information1 = {
        "video_file_name": "file_name1",
        "frame_number": 1,
        "frame_file_path": "path1",
    }
    frame_service_information2 = {
        "video_file_name": "file_name2",
        "frame_number": 3,
        "frame_file_path": "path2",
    }
    create_frame_service_information(app, db, **frame_service_information1)
    create_frame_service_information(app, db, **frame_service_information2)

    response = client.get('/api/saved_frames')
    assert response.status_code == 200
    assert response.get_json() == [ frame_service_information1, frame_service_information2 ]

    # check idempotent
    response = client.get('/api/saved_frames')
    assert response.status_code == 200
    assert response.get_json() == [ frame_service_information1, frame_service_information2 ]


def test_route_saved_frames_new_file_without_body(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с пустым телом запроса.

    Args:
        client: Тестовый клиент.
    """
    response = client.post('/api/saved_frames/new_frame')
    assert response.status_code == 400


def test_route_saved_frames_new_file_empty_json_body(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с отсутствующими параметрами.

    Args:
        client: Тестовый клиент.
    """
    response = client.post('/api/saved_frames/new_frame', json={})
    assert response.status_code == 400
    assert response.get_json() == {
        'file_path': 'Required field.',
        'frame_number': 'Required field.'
    }


def test_route_saved_frames_new_file_field_types(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с параметрами неправильного типа.

    Args:
        client: Тестовый клиент.
    """
    response = client.post('/api/saved_frames/new_frame', json={
        'file_path': None,
        'frame_number': '1'
    })
    assert response.status_code == 400
    assert response.get_json() == {
        'file_path': 'Required string type.',
        'frame_number': 'Required number type.'
    }


def test_route_saved_frames_new_file_constraints(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с недопустимыми значениями параметров.

    Args:
        client: Тестовый клиент.
    """
    response = client.post('/api/saved_frames/new_frame', json={
        'file_path': '',
        'frame_number': -1
    })
    assert response.status_code == 400
    assert response.get_json() == {
        'file_path': 'Shorter than minimum length 1.',
        'frame_number': 'Less than minimum value 0.'
    }


def test_route_saved_frames_new_file_file_doesnt_exist(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с несуществующим именем файла.

    Args:
        client: Тестовый клиент.
    """
    body = {
        'file_path': 'sampl.mp4', # имя видеофайла
        'frame_number': 1
    }
    response = client.post('/api/saved_frames/new_frame', json=body)
    assert response.status_code == 400
    assert response.get_json() == {
        "message": "Frame doesn't exist."
    }


def test_route_saved_frames_new_file_frame_doesnt_exist(
        client: 'FlaskClient',
        clean_frames_dir: None
):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file с несуществующим фреймом.

    Args:
        client: Тестовый клиент.
        clean_frames_dir: Вызов фикстуры для удаления всех файлов в каталоге с фреймами перед выполнением теста.
    """
    body = {
        'file_path': 'sample-1.mp4', # имя видеофайла
        'frame_number': 10
    }
    response = client.post('/api/saved_frames/new_frame', json=body)
    assert response.status_code == 400
    assert response.get_json() == {
        "message": "Frame doesn't exist."
    }


def test_route_saved_frames_create(
        client: 'FlaskClient',
        app: 'Flask',
        db: 'SQLAlchemy',
        clean_frames_dir: None
):
    """Функция проверяет ответ сервера по маршруту /api/saved_frames/new_file при сохранении служебной информации в БД.

    Args:
        client: Тестовый клиент.
        db: Вызов фикстуры для очистки базы данных перед выполнением теста.
        clean_frames_dir: Вызов фикстуры для удаления всех файлов в каталоге с фреймами перед выполнением теста.
    """
    # make frames
    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=0')
    assert response.status_code == 200

    request_body = {
        'file_path': 'sample-1.mp4', # имя видеофайла
        'frame_number': 1
    }
    response = client.post('/api/saved_frames/new_frame', json=request_body)

    frames_dir_path = Config().flask['FRAMES_DIR_PATH']
    assert response.status_code == 201
    assert response.get_json() == {
        'file_path': 'sample-1.mp4',
        'frame_number': 1,
        "frame_path": os.path.join(frames_dir_path, 'sample-1.mp4', '1.png')
    }

    # read record from database
    with app.app_context():
        frame_service_informations = db.session.execute(select(FrameServiceInformation)).scalars().all()

    assert len(frame_service_informations) == 1
    assert frame_service_informations[0].video_file_name == 'sample-1.mp4'
    assert frame_service_informations[0].frame_number == 1
    assert frame_service_informations[0].frame_file_path == os.path.join(frames_dir_path, 'sample-1.mp4', '1.png')

    # repeat request
    response = client.post('/api/saved_frames/new_frame', json=request_body)
    assert response.status_code == 400

    with app.app_context():
        frame_service_informations = db.session.execute(select(FrameServiceInformation)).scalars().all()
    assert len(frame_service_informations) == 1
    assert frame_service_informations[0].video_file_name == 'sample-1.mp4'
    assert frame_service_informations[0].frame_number == 1
    assert frame_service_informations[0].frame_file_path == os.path.join(frames_dir_path, 'sample-1.mp4', '1.png')