import os

import cv2
from flask_restx import Resource, Namespace, fields, reqparse

from src.utils.config import Config
from src.utils.get_frames import extract_frame


frames_ns = Namespace('frames')


# https://flask-restx.readthedocs.io/en/latest/parsing.html#argument-locations
# location: args, form, headers, cookie, files
parser = reqparse.RequestParser()
parser.add_argument('file_name', type=str, required=True, location='args',
                    help='Имя видеофайла')
parser.add_argument('time_in_video', type=int, required=True, location='args',
                    help='Время от начала видеофайла в секундах')


FrameOutModel = frames_ns.model('Frame Out Model', {
    "first_frame": fields.String,
    "file_paths": fields.List(fields.String)
})


@frames_ns.route('')
class FrameView(Resource):
    @frames_ns.expect(parser, validate=True)
    @frames_ns.marshal_with(FrameOutModel)
    @frames_ns.response(500, 'Internal Server Error', frames_ns.model('', {
        'message': fields.String,
    }))
    def get(self):
        """Возвращает номер первого кадра и массив строк с маршрутами к файлам с
        кадрами.

        Params:
            file_name (str): Имя видеофайла.
            time_in_video (int): Время от начала видеофайла в секундах.
        """
        args = parser.parse_args() # req=True

        file_name = args['file_name']
        time_in_video = args['time_in_video']

        # file access by relative paths ../../../something
        simple_filename_check = lambda x: os.pathsep not in x and ".." not in x

        # field constraints
        constraint_failed = {}
        if len(file_name) == 0:
            constraint_failed['file_name'] = 'Shorter than minimum length 1.'
        if not simple_filename_check(file_name):
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
                return {'message': 'Frame directory is file'}, 500

            frame_paths = []
            for (i, frame) in enumerate(frames):
                frame_name = f'{first_frame + i}.png'
                frame_path = os.path.join(frame_dir, frame_name)
                frame_paths.append(frame_path)
                cv2.imwrite(frame_path, frame)
        except:
            return {'message': 'Something went wrong'}, 500

        response_data = {
            "first_frame": first_frame,
            "file_paths": frame_paths
        }
        return response_data
