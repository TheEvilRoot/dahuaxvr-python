from datetime import datetime
from queue import Queue
from threading import Thread

import cv2
import face_recognition

from dahuaxvr.camera_stream import CameraStream


class Player:

    def __init__(self, cam: CameraStream, uri: str):
        self.face_locations = []
        self.start_time = None
        self.cam = cam
        self.uri = uri
        self.face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.write_queue = Queue()
        self.write_thread = Thread(target=self.writer)

    def run(self):
        self.cam.GetFrameStream(
            uri=self.uri,
            processor=self.processor,
            handler=self.handler
        )
        cv2.destroyAllWindows()
        self.write_queue.put(None)

    def writer(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        index = 0
        out = None
        while True:
            frame = self.write_queue.get()
            if out is None:
                out = cv2.VideoWriter('/tmp/output.mp4', fourcc, 30, frame.shape[:2][::-1])
            if frame is None:
                break
            out.write(frame)
            index += 1
            fps = index / (datetime.now().timestamp() - self.start_time.timestamp()) \
                if self.start_time is not None else 0
            if index % 100 == 0:
                print('writer fps = %.1f' % fps)
        out.release()

    def increase_brightness(self, img, value=30):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value

        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return img

    def increase_contrast(self, img):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
        cl = clahe.apply(l_channel)
        limg = cv2.merge((cl, a, b))
        enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return enhanced_img

    def processor(self, frame, index):
        if index % 1 == 0:
            # frame = self.increase_contrast(self.increase_brightness(frame))
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            self.face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
        for (top, right, bottom, left) in self.face_locations:
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, 'name', (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        fps = index / (datetime.now().timestamp() - self.start_time.timestamp()) if self.start_time is not None else 0
        fps = '%.1f' % fps
        cv2.putText(frame, fps, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, 2)
        return frame

    def handler(self, frame, index):
        if not self.write_thread.is_alive():
            self.write_thread.start()
        if self.start_time is None:
            self.start_time = datetime.now()
        cv2.imshow('Video', frame)
        self.write_queue.put(frame)
        return not (cv2.waitKey(20) & 0xFF == ord('q'))
