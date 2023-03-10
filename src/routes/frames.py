import os
import json

import cv2
from flask import Blueprint, Response, request

from src.utils.config import Config
from src.utils.get_frames import extract_frame

frames_bp = Blueprint('frames', __name__)


@frames_bp.route('', methods=['GET'])
def get_frames():
    """Возвращает номер первого кадра и массив строк с маршрутами к файлам с
    кадрами.

    Params:
        file_name (str): Имя видеофайла.
        time_in_video (int): Время от начала видеофайла в секундах.
    """
    file_name = request.args.get('file_name')
    time_in_video = request.args.get('time_in_video')

    # check required fields
    required_fields = {}
    if file_name is None:
        required_fields['file_name'] = 'Required field.'
    if time_in_video is None:
        required_fields['time_in_video'] = 'Required field.'
    if len(required_fields) > 0:
        return required_fields, 400

    # check field types
    try:
        time_in_video = int(time_in_video)
    except Exception:
        return {"time_in_video": "Required number type"}, 400

    # file access by relative paths ../../../something
    simple_filename_check = lambda x: os.pathsep not in x and ".." not in x

    # field constraints
    constraint_failed = {}
    if len(file_name) == 0:
        constraint_failed['file_name'] = 'Shorter than minimum length 1.'
    elif not simple_filename_check(file_name):
        constraint_failed['file_name'] = 'Forbidden file name.'
    if time_in_video < 0:
        constraint_failed['time_in_video'] = 'Less than minimum value 0.'
    if len(constraint_failed) > 0:
        return constraint_failed, 400

    # check the existence of the file
    config = Config()
    video_path = os.path.join(config.flask['VIDEOS_DIR_PATH'], file_name)
    if not os.path.isfile(video_path):
        return {"file_name": "File doesn't exist"}, 400

    # extract frames
    first_frame, frames = extract_frame(video_path, time_in_video)
    if len(frames) != config.flask['SAVE_FRAMES_COUNT'] or first_frame is None:
        return {"message": "Failed to extract frames."}, 500  # split with 400

    # save images
    try:
        frame_dir = os.path.join(config.flask['FRAMES_DIR_PATH'], file_name)
        if not os.path.exists(frame_dir):
            os.mkdir(frame_dir)
        elif os.path.isfile(frame_dir):
            return 'Frame directory is file', 500

        frame_paths = []
        for (i, frame) in enumerate(frames):
            frame_name = f'{first_frame + i}.png'
            frame_path = os.path.join(frame_dir, frame_name)
            frame_paths.append(frame_path)
            cv2.imwrite(frame_path, frame)
    except Exception:
        return 'Something went wrong', 500

    response_data = {
        "first_frame": first_frame,
        "file_paths": frame_paths
    }
    return Response(json.dumps(response_data), 200, mimetype='application/json')
