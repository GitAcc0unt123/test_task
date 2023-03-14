import os
from http import HTTPStatus

from flask import request
from flask_restx import Resource, Namespace, fields, abort
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models import db, FrameServiceInformation
from src.utils.config import Config


saved_frames_ns = Namespace('saved frames')


SavedFramesListModel = saved_frames_ns.model('Saved Frames List Model', {
    "video_file_name": fields.String,
    "frame_number": fields.Integer,
    "frame_file_path": fields.String,
})

# https://flask-restx.readthedocs.io/en/latest/swagger.html#documenting-the-fields
SavedFramesInModel = saved_frames_ns.model('Saved Frames In Model', {
    "file_path": fields.String(required=True, min_length=1),
    "frame_number": fields.Integer(required=True, min=0)
})

SavedFramesOutModel = saved_frames_ns.model('Saved Frames Out Model', {
    "file_path": fields.String,
    "frame_number": fields.Integer,
    "frame_path": fields.String
})


@saved_frames_ns.route("")
class VideoView(Resource):

    @saved_frames_ns.marshal_list_with(SavedFramesListModel)
    @saved_frames_ns.response(500, 'Internal Server Error',
                              saved_frames_ns.model('', {
                                'message': fields.String,
    }))
    def get(self):
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
            return response_data
        except:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, 'Something went wrong')
            #return {'message': 'Something went wrong'}, 500


    @saved_frames_ns.expect(SavedFramesInModel, validate=True)
    @saved_frames_ns.marshal_with(SavedFramesOutModel, code=201)
    def post(self):
        """Сохраняет в БД служебную информацию о ранее сохранённом кадре.

        Params:
            file_path (str): Имя видеофайла
            frame_number (int): Номер кадра
        """
        request_json = request.get_json()

        video_file_name = request_json['file_path']
        frame_number = request_json['frame_number']

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
            return response
        except IntegrityError:
            db.session.rollback()
            return {}, HTTPStatus.BAD_REQUEST
        except:
            db.session.rollback()
            return {}, HTTPStatus.INTERNAL_SERVER_ERROR
