import os
from typing import TYPE_CHECKING

from src.utils.config import Config

if TYPE_CHECKING:
    from flask.testing import FlaskClient


def test_route_frames_empty_query(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames при отсутствующих параметрах в query string.

    Args:
        client: Тестовый клиент.
    """
    response = client.get('/api/frames')
    assert response.status_code == 400
    assert response.get_json() == {
        "file_name": "Required field.",
        "time_in_video": "Required field."
    }


def test_route_frames_file_doesnt_exist(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames при отсутствии файла указанного в параметре file_name.

    Args:
        client: Тестовый клиент.
    """
    response = client.get('/api/frames?file_name=404&time_in_video=1')
    assert response.status_code == 400
    assert response.get_json() == {
        "file_name": "File doesn't exist"
    }


def test_route_frames_file_name_len_0(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames при пустом значении параметра file_name.

    Args:
        client: Тестовый клиент.
    """
    response = client.get(f'/api/frames?file_name=&time_in_video=1')
    assert response.status_code == 400
    assert response.get_json() == {
        "file_name": "Shorter than minimum length 1."
    }


def test_route_frames_forbidden_file_name(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames при недопустимом значении параметра file_name.

    Args:
        client: Тестовый клиент.
    """
    response = client.get(f'/api/frames?file_name=../parent_dir.mp4&time_in_video=1')
    assert response.status_code == 400
    assert response.get_json() == {
        "file_name": "Forbidden file name."
    }


def test_route_frames_time_not_int(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames при нечисловом значении параметра time_in_video.

    Args:
        client: Тестовый клиент.
    """
    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=kl')
    assert response.status_code == 400
    assert response.get_json() == {
        "time_in_video": "Required number type"
    }


def test_route_frames_invalid_time(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames
       при отрицательном числовом значении параметра time_in_video.

    Args:
        client: Тестовый клиент.
    """
    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=-1')
    assert response.status_code == 400
    assert response.get_json() == {
        "time_in_video": "Less than minimum value 0."
    }


def test_route_frames_big_time(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames при значении
       параметра time_in_video заведомо большем чем число кадров в видео.

    Args:
        client: Тестовый клиент.
    """
    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=999999')
    assert response.status_code == 500
    assert response.get_json() == {
        "message": "Failed to extract frames."
    }


def test_route_frames_corrupted_file(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames при повреждении файла указанного в параметре file_name.

    Args:
        client: Тестовый клиент.
    """
    response = client.get('/api/frames?file_name=corrupted_file.mp4&time_in_video=1')
    assert response.status_code == 500
    assert response.get_json() == {
        "message": "Failed to extract frames."
    }


def test_route_frames_file_name_with_space(client: 'FlaskClient'):
    """Функция проверяет ответ сервера по маршруту /api/frames при пробеле в значении параметра file_name.

    Args:
        client: Тестовый клиент.
    """
    config = Config()
    frames_dir_path = config.flask['FRAMES_DIR_PATH']
    save_frames_count = config.flask['SAVE_FRAMES_COUNT']

    response = client.get(f'/api/frames?file_name=sample 0.mp4&time_in_video=1')
    assert response.status_code == 200
    assert response.get_json() == {
        "first_frame": 30,
        "file_paths": [
            f"{frames_dir_path}/sample 0.mp4/{i}.png"
            for i in range(30, 30 + save_frames_count)
        ]
    }
    # check created files in FRAMES_DIR_PATH
    file_names = set( os.listdir(f"{frames_dir_path}/sample 0.mp4") )
    assert file_names == set( f"{i}.png" for i in range(30, 30 + save_frames_count) )


def test_route_frames_en_filename_sec_0(client: 'FlaskClient', clean_frames_dir: None):
    """Функция проверяет ответ сервера по маршруту /api/frames при указании корректных значений параметров.

    Args:
        client: Тестовый клиент.
        clean_frames_dir: Вызов фикстуры для удаления всех файлов в каталоге с фреймами перед выполнением теста.
    """
    config = Config()
    frames_dir_path = config.flask['FRAMES_DIR_PATH']
    save_frames_count = config.flask['SAVE_FRAMES_COUNT']

    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=0')
    assert response.status_code == 200
    assert response.get_json() == {
        "first_frame": 0,
        "file_paths": [
            f"{frames_dir_path}/sample-1.mp4/{i}.png"
            for i in range(save_frames_count)
        ]
    }
    # check created files in FRAMES_DIR_PATH
    file_names = set( os.listdir(f"{frames_dir_path}/sample-1.mp4") )
    assert file_names == set( f"{i}.png" for i in range(save_frames_count) )

    # check idempotent
    response2 = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=0')
    assert response2.status_code == 200
    assert response2.get_json() == {
        "first_frame": 0,
        "file_paths": [
            f"{frames_dir_path}/sample-1.mp4/{i}.png"
            for i in range(save_frames_count)
        ]
    }
    file_names = set( os.listdir(f"{frames_dir_path}/sample-1.mp4") )
    assert file_names == set( f"{i}.png" for i in range(save_frames_count) )


def test_route_frames_en_filename_sec_2_fps_30(client: 'FlaskClient', clean_frames_dir: None):
    """Функция проверяет ответ сервера по маршруту /api/frames при указании корректных значений параметров.

    Args:
        client: Тестовый клиент.
        clean_frames_dir: Вызов фикстуры для удаления всех файлов в каталоге с фреймами перед выполнением теста.
    """
    config = Config()
    frames_dir_path = config.flask['FRAMES_DIR_PATH']
    save_frames_count = config.flask['SAVE_FRAMES_COUNT']

    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=2')
    assert response.status_code == 200
    assert response.get_json() == {
        "first_frame": 60,
        "file_paths": [
            f"{frames_dir_path}/sample-1.mp4/{i}.png"
            for i in range(60, 60 + save_frames_count)
        ]
    }
    # check created files in FRAMES_DIR_PATH
    file_names = set( os.listdir(f"{frames_dir_path}/sample-1.mp4") )
    assert set(file_names) == set( f"{i}.png" for i in range(60, 60 + save_frames_count) )

    # check idempotent
    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=2')
    assert response.status_code == 200
    assert response.get_json() == {
        "first_frame": 60,
        "file_paths": [
            f"{frames_dir_path}/sample-1.mp4/{i}.png"
            for i in range(60, 60 + save_frames_count)
        ]
    }
    file_names = set( os.listdir(f"{frames_dir_path}/sample-1.mp4") )
    assert set(file_names) == set( f"{i}.png" for i in range(60, 60 + save_frames_count) )


def test_route_frames_en_filename_sec_6(client: 'FlaskClient', clean_frames_dir: None):
    """Функция проверяет ответ сервера по маршруту /api/frames при указании корректных значений параметров.

    Args:
        client: Тестовый клиент.
        clean_frames_dir: Вызов фикстуры для удаления всех файлов в каталоге с фреймами перед выполнением теста.
    """
    response = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=6')
    assert response.status_code == 500
    assert response.get_json() == {
        "message": "Failed to extract frames."
    }

    # check idempotent
    response2 = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=6')
    response2 = client.get('/api/frames?file_name=sample-1.mp4&time_in_video=6')
    assert response2.status_code == 500
    assert response2.get_json() == {
        "message": "Failed to extract frames."
    }


def test_route_frames_ru_filename_sec_0(client: 'FlaskClient', clean_frames_dir: None):
    """Функция проверяет ответ сервера по маршруту /api/frames при указании корректных значений параметров.

    Args:
        client: Тестовый клиент.
        clean_frames_dir: Вызов фикстуры для удаления всех файлов в каталоге с фреймами перед выполнением теста.
    """
    config = Config()
    frames_dir_path = config.flask['FRAMES_DIR_PATH']
    save_frames_count = config.flask['SAVE_FRAMES_COUNT']

    response = client.get('/api/frames?file_name=пример-1.mp4&time_in_video=0')
    assert response.status_code == 200
    assert response.get_json() == {
        "first_frame": 0,
        "file_paths": [
            f"{frames_dir_path}/пример-1.mp4/{i}.png"
            for i in range(save_frames_count)
        ]
    }
    # check created files in FRAMES_DIR_PATH
    file_names = set( os.listdir(f"{frames_dir_path}/пример-1.mp4") )
    assert file_names == set( f"{i}.png" for i in range(save_frames_count) )

    # check idempotent
    response = client.get('/api/frames?file_name=пример-1.mp4&time_in_video=0')
    response = client.get('/api/frames?file_name=пример-1.mp4&time_in_video=0')
    assert response.status_code == 200
    assert response.get_json() == {
        "first_frame": 0,
        "file_paths": [
            f"{frames_dir_path}/пример-1.mp4/{i}.png"
            for i in range(save_frames_count)
        ]
    }
    file_names = set( os.listdir(f"{frames_dir_path}/пример-1.mp4") )
    assert file_names == set( f"{i}.png" for i in range(save_frames_count) )
