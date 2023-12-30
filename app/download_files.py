"""
Usage example:
$ PYTHONPATH=. python3 app/download_files.py -u admin --password-raw password 192.168.1.2 -o /Volumes/Storage/CCTV/ --remove-first-parents 3
"""

import os.path
from datetime import datetime, timedelta

from requests.auth import HTTPDigestAuth

from app.show_camera import Player
from dahuaxvr.camera_stream import CameraStream
from dahuaxvr.cgi.config_manager import ConfigManagerCgi
from dahuaxvr.cgi.load_file import LoadFileCgi
from dahuaxvr.cgi.media_file_find import MediaFileFindCgi
from dahuaxvr.model.media_file_finder import MediaFileFinder
from tqdm import tqdm
import pathlib

def get_out_path(file_path: str, out_dir: str, remove_first_parents: int):
    rel_file_path = pathlib.Path(*pathlib.Path(file_path).parts[remove_first_parents:]) 
    return os.path.join(out_dir, rel_file_path)

def download_batch(lfcgi: LoadFileCgi, cgi: MediaFileFindCgi, initial_date: datetime, start_offset: int,
                   end_offset: int, out_dir: str, remove_first_parents: int):
    print(f'Loading batch {start_offset}:{end_offset} from {initial_date}')
    with MediaFileFinder(cgi) as finder:
        files = finder.find_iter(
            start_date=initial_date - timedelta(hours=start_offset),
            end_date=initial_date - timedelta(hours=end_offset),
            types=["mp4"]
        )
        files = list(files)
    print(f'{start_offset}:{end_offset} {len(files)} files fetched')
    for index, file in tqdm(enumerate(files)):
        file_path = file['FilePath']
        out_file_path = get_put_path(fle_path, out_dir, remove_first_parents)
        print(f'{index:>2}. {file["StartTime"]} - {file["EndTime"]} | {file["VideoStream"]} {file_path} -> {out_file_path}')
        if os.path.exists(out_file_path):
            print(f'{out_file_path} already exists, skipping')
            continue
        os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
        content = lfcgi.load_file(file_path)
        with open(out_file_path, 'w+b') as handle:
            handle.write(content)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='IP Address or domain of Dahua XVR')
    parser.add_argument('-u', '--user', dest='user', help='User name')
    parser.add_argument('--password-raw', dest='password', default=None)
    parser.add_argument('-o', '--output-dir', dest='output_dir', default='.')
    parser.add_argument('--remove-first-parents', dest='remove_first_parents', default=0, type=int, help='Remove first parents in file paths. Like --remove-first-parents=3 with path /mnt/sd/29-11-2012/001/dav/ will make path like 29-11-20223/001/dav/')
    args = parser.parse_args()
    auth = HTTPDigestAuth(args.user, args.password)
    cgi = MediaFileFindCgi(f'http://{args.host}', auth)
    lfcgi = LoadFileCgi(f'http://{args.host}', auth)

    step = 12
    start_offset = step
    end_offset = 0

    initial_date = datetime.now()
    for i in range(31*24//step):
        try:
            download_batch(lfcgi, cgi, initial_date, start_offset, end_offset, args.output_dir, args_remove_first_parents)
        except Exception as e:
            print(f'Error occurred loading batch {start_offset}:{end_offset}: {e}')
            raise e
        end_offset += step
        start_offset += step


if __name__ == '__main__':
    main()
