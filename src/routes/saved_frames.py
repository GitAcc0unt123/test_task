import os
import json

from flask import Blueprint, Response, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models import db, FrameServiceInformation
from src.utils.config import Config

saved_frames_bp = Blueprint('saved_frames', __name__)


@saved_frames_bp.route('', methods=['GET'])
def get_saved_frames():
    """Возвращает список сохранённых кадров со служебной информацией
       из базы данных.
    """
    try:
        stmt = select(FrameServiceInformation)
        frame_service_information = db.session.execute(stmt).scalars().all()
        response_data = [
            {
                "video_file_name": x.video_file_name,
                "frame_number": x.frame_number,
                "frame_file_path": x.frame_file_path,
            }
            for x in frame_service_information
        ]
        response_data = json.dumps(response_data)
        return Response(response_data, 200, mimetype='application/json')
    except:
        return 'Something went wrong', 500


@saved_frames_bp.route('new_frame', methods=['POST'])
def create_saved_frame():
    """Сохраняет в БД служебную информацию о ранее сохранённом кадре.

    Params:
        file_path (str): Имя видеофайла
        frame_number (int): Номер кадра
    """
    request_json = request.json

    # check required fields
    required_fields = ['file_path', 'frame_number']
    required_fields = {
        f: 'Required field.'
        for f in required_fields
        if f not in request_json
    }
    if len(required_fields) > 0:
        return required_fields, 400

    # check field types
    video_file_name = request_json['file_path']
    frame_number = request_json['frame_number']
    type_validation_failed = {}
    if not isinstance(video_file_name, str):
        type_validation_failed['file_path'] = 'Required string type.'
    if not isinstance(frame_number, int):
        type_validation_failed['frame_number'] = 'Required number type.'
    if len(type_validation_failed) > 0:
        return type_validation_failed, 400

    # field constraints
    constraint_failed = {}
    if len(video_file_name) == 0:
        constraint_failed['file_path'] = 'Shorter than minimum length 1.'
    if frame_number < 0:
        constraint_failed['frame_number'] = 'Less than minimum value 0.'
    if len(constraint_failed) > 0:
        return constraint_failed, 400

    try:
        # check frame
        frame_dir_path = Config().flask['FRAMES_DIR_PATH']
        frame_name = f'{frame_number}.png'
        frame_path = os.path.join(frame_dir_path, video_file_name, frame_name)
        if not os.path.isfile(frame_path):
            return {"message": "Frame doesn't exist."}, 400

        frame_service_information = FrameServiceInformation(
            video_file_name,
            frame_number,
            frame_path
        )
        db.session.add(frame_service_information)
        db.session.commit()
        response = {
            "file_path": frame_service_information.video_file_name,
            "frame_number": frame_service_information.frame_number,
            "frame_path": frame_service_information.frame_file_path
        }
        return response, 201
    except IntegrityError:
        db.session.rollback()
        return Response(status=400)
    except:
        db.session.rollback()
        return Response(status=500)
