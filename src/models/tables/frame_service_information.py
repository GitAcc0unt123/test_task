from src.models.database import db


class FrameServiceInformation(db.Model):
    """Служебная информация о вырезанном кадре.

    Attributes:
        video_file_name: Имя исходного видеофайла.
        frame_number: Порядковый номер вырезанного кадра от начала файла.
        frame_file_path: Полный путь к файлу с вырезанный кадром.
    """
    __tablename__ = "frame_service_information"

    video_file_name: str = db.Column(db.String(), primary_key=True)
    frame_number: int = db.Column(db.Integer, primary_key=True)
    frame_file_path: str = db.Column(db.String(), nullable=False)

    def __init__(self,
                 video_file_name: str,
                 frame_number: int,
                 frame_file_path: str,
                 ) -> None:
        """Инициализирует экземпляр класса.

        Args:
            video_file_name: Имя исходного видеофайла.
            frame_number: Порядковый номер вырезанного кадра от начала файла.
            frame_file_path: Полный путь к файлу с вырезанный кадром.
        """
        self.video_file_name = video_file_name
        self.frame_number = frame_number
        self.frame_file_path = frame_file_path
