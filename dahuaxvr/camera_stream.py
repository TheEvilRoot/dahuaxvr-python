from typing import Callable

import cv2


class CameraStream:

    def __init__(self, host: str, port: int, authorization):
        self.host = host
        self.port = port
        self.authorization = authorization

    def GetFrameStream(self, uri: str,
                       processor: Callable[[cv2.typing.MatLike, int], cv2.typing.MatLike],
                       handler: Callable[[cv2.typing.MatLike, int], bool]):
        cap = self.GetOpenCvStream(uri)
        index = 0
        while cap.isOpened():
            index += 1
            ret, frame = cap.read()
            frame = processor(frame, index)
            if not handler(frame, index):
                break
        cap.release()

    def GetStreamUri(self, channel: int, sub_type: int):
        return f'rtsp://{self.authorization.username}:{self.authorization.password}@{self.host}:{self.port}/cam/realmonitor?channel={channel}&subtype={sub_type}'

    def GetFileUri(self, file: dict):
        return f'rtsp://{self.authorization.username}:{self.authorization.password}@{self.host}:{self.port}/{file["FilePath"]}'

    def GetOpenCvStream(self, uri: str):
        return cv2.VideoCapture(uri)
