from requests.auth import HTTPDigestAuth

from app.player import Player
from dahuaxvr.camera_stream import CameraStream
from dahuaxvr.cgi.config_manager import ConfigManagerCgi


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='IP Address or domain of Dahua XVR')
    parser.add_argument('-u', '--user', dest='user', help='User name')
    parser.add_argument('--password-raw', dest='password', default=None)
    parser.add_argument('-c', '--channel', dest='channel', default=1)
    parser.add_argument('-s', '--subtype', dest='sub_type', default=1)
    args = parser.parse_args()

    auth = HTTPDigestAuth(args.user, args.password)
    cgi = ConfigManagerCgi(f'http://{args.host}', auth)
    rtsp_config = cgi.GetRTSPConfig()
    cam = CameraStream(args.host, rtsp_config['table']['RTSP']['Port'], auth)
    uri = cam.GetStreamUri(channel=args.channel, sub_type=args.sub_type)
    player = Player(cam, uri)
    player.run()


if __name__ == '__main__':
    main()
