import cv2
from requests.auth import HTTPDigestAuth
from queue import Queue
from threading import Thread

from dahuaxvr.camera_stream import CameraStream
from dahuaxvr.cgi.config_manager import ConfigManagerCgi


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='IP Address or domain of Dahua XVR')
    parser.add_argument('-u', '--user', dest='user', help='User name')
    parser.add_argument('--password-raw', dest='password', default=None)
    args = parser.parse_args()

    auth = HTTPDigestAuth(args.user, args.password)
    cgi = ConfigManagerCgi(f'http://{args.host}', auth)
    rtsp_config = cgi.GetRTSPConfig()
    cam = CameraStream(args.host, rtsp_config['table']['RTSP']['Port'], auth)
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    write_queue = Queue()

    def writer():
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('/tmp/output.avi', fourcc, 60, (640, 480))
        while True:
            frame = write_queue.get()
            if frame is None:
                break
            out.write(frame)
        out.release()

    write_thread = Thread(target=writer)

    def processor(frame, index):
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = face_classifier.detectMultiScale(
            gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        for (x, y, w, h) in face:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
        return frame

    def handler(frame, index):
        if not write_thread.is_alive():
            write_thread.start()
        cv2.imshow('Video', frame)
        write_queue.put(frame)
        return not (cv2.waitKey(20) & 0xFF == ord('q'))

    cam.GetFrameStream(
        uri=cam.GetStreamUri(channel=1, sub_type=1),
        processor=processor,
        handler=handler
    )
    cv2.destroyAllWindows()
    write_queue.put(None)


if __name__ == '__main__':
    main()
