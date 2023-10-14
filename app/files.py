from datetime import datetime, timedelta

from requests.auth import HTTPDigestAuth

from app.show_camera import Player
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
            start_date=datetime.now() - timedelta(hours=5),
            end_date=datetime.now()
        )
        files = list(files)

    while True:
        print(f'Found {len(files)} files')
        for index, file in enumerate(files):
            print(f'{index:>2}. {file["StartTime"]} - {file["EndTime"]} | {file["VideoStream"]}')
        try:
            index = int(input('Index > '))
            file = files[index]
            config_cgi = ConfigManagerCgi(f'http://{args.host}', auth)
            rtsp_config = config_cgi.GetRTSPConfig()
            cam = CameraStream(args.host, rtsp_config['table']['RTSP']['Port'], auth)
            player = Player(cam, cam.GetFileUri(file))
            player.run()
        except KeyboardInterrupt:
            print('Exiting.')
            break
        except:
            print('Error occurred!')


if __name__ == '__main__':
    main()
