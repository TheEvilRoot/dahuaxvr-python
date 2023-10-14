from datetime import datetime, timedelta

import cv2
from requests.auth import HTTPDigestAuth

from dahuaxvr.camera_stream import CameraStream
from dahuaxvr.cgi.config_manager import ConfigManagerCgi
from dahuaxvr.cgi.media_file_find import MediaFileFindCgi
from dahuaxvr.model.media_file_finder import MediaFileFinder


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='IP Address or domain of Dahua XVR')
    parser.add_argument('-u', '--user', dest='user', help='User name')
    parser.add_argument('--password-raw', dest='password', default=None)
    args = parser.parse_args()
    auth = HTTPDigestAuth(args.user, args.password)
    cgi = MediaFileFindCgi(f'http://{args.host}', auth)
    with MediaFileFinder(cgi) as finder:
        files = finder.find_iter(
            start_date=datetime.now() - timedelta(days=2),
            end_date=datetime.now()
        )
        for file in files:
            config_cgi = ConfigManagerCgi(f'http://{args.host}', auth)
            rtsp_config = config_cgi.GetRTSPConfig()
            cam = CameraStream(args.host, rtsp_config['table']['RTSP']['Port'], auth)
            def handler(frame, index):
                cv2.imshow(file['FilePath'], frame)
                return not (cv2.waitKey(20) & 0xFF == ord('q'))
            cam.GetFrameStream(
                uri=cam.GetFileUri(file),
                processor=lambda frame, index: frame,
                handler=handler
            )
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    main()
