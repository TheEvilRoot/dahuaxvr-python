from datetime import datetime, timedelta

from requests.auth import HTTPDigestAuth

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
        print(
            finder.cgi.StartFind(finder.handle, 1, [], [], datetime.now() - timedelta(days=2), datetime.now(), ['mp4'],
                                 []))
        print(finder.cgi.FindNextFile(finder.handle, 10))


if __name__ == '__main__':
    main()
