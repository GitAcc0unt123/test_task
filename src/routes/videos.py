import os
import json

from flask import Blueprint, Response

from src.utils.config import Config


videos_bp = Blueprint('videos', __name__)


@videos_bp.route('', methods=['GET'])
def get_video_list():
    """Возвращает список имён файлов и полный путь к ним из указанного
    в конфигурационном файле каталога с видео.
    """
    video_dir_path = Config().flask['VIDEOS_DIR_PATH']
    try:
        response_data = [
            {
                "file_name": filename,
                "file_path": os.path.join(video_dir_path, filename)
            }
            for filename in os.listdir(video_dir_path)
            if os.path.isfile(os.path.join(video_dir_path, filename))
        ]
        response_data = json.dumps(response_data)
        return Response(response_data, 200, mimetype='application/json')
    except Exception:
        return Response('Something went wrong', 500)
