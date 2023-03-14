import os
from http import HTTPStatus

from flask_restx import Resource, Namespace, fields, abort
#from werkzeug.exceptions import InternalServerError

from src.utils.config import Config


videos_ns = Namespace('videos')


VideoModel = videos_ns.model('Video Model', {
    'file_name': fields.String,
    'file_path': fields.String,
})


@videos_ns.route("")
class VideoView(Resource):
    @videos_ns.marshal_list_with(VideoModel)
    @videos_ns.response(500, 'Internal Server Error', videos_ns.model('', {
        'message': fields.String,
    }))
    def get(self):
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
            return response_data
        except:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, 'Something went wrong')
