from typing import Callable

import cv2


class CameraStream:

    def __init__(self, host: str, port: int, authorization):
        self.host = host
        self.port = port
        self.authorization = authorization

    def GetFrameStream(self, channel: int, sub_type: int,
                       processor: Callable[[cv2.typing.MatLike, int], cv2.typing.MatLike],
                       handler: Callable[[cv2.typing.MatLike, int], bool]):
        cap = self.GetOpenCvStream(channel, sub_type)
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

    def GetOpenCvStream(self, channel: int, sub_type: int):
        cap = cv2.VideoCapture(self.GetStreamUri(channel, sub_type))
        return cap