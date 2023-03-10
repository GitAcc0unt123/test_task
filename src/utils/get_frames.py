from typing import List, Tuple, Optional, TYPE_CHECKING

import cv2

from src.utils.config import Config

if TYPE_CHECKING:
    from numpy import ndarray


def extract_frame(
        video_path: str,
        time_in_video: int
    ) -> Tuple[Optional[int], List['ndarray']]:
    """Функция для извлечения кадров из видеофайла.

    Args:
        video_path: Полный путь к видеофайлу.
        time_in_video: Время от начала видеофайла в секундах.

    Returns:
        Номер первого извлечённого кадра и список извлечённых кадров.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not cap.isOpened():
        return
    frame_counter = 0
    images = []
    save_frames_count = Config().flask['SAVE_FRAMES_COUNT']
    while frame_counter < total_frames:
        success, image = cap.read()
        frame_counter += 1
        if not success:
            continue
        # зная количество кадров в секунду (fps), здесь можно определить кадр,
        # соответствующий заданному времени на видео
        if time_in_video * fps + save_frames_count < frame_counter:
            break

        if time_in_video * fps < frame_counter:
            images.append(image)

    if len(images) == save_frames_count:
        return int(time_in_video * fps), images
    else:
        return None, []
