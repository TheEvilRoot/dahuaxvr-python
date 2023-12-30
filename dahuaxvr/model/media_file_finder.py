from datetime import datetime
from typing import List

from dahuaxvr.cgi.media_file_find import MediaFileFindCgi


class MediaFileFinder:
    def __init__(self, cgi: MediaFileFindCgi,
                 ):
        self.cgi = cgi
        self.handle = None
        self.closed = True
        self.destroyed = False

    def find_iter(self,
                  start_date: datetime,
                  end_date: datetime,
                  channel: int = 1,
                  dirs: List[str] = None,
                  events: List[str] = None,
                  types: List[str] = None,
                  flags: List[str] = None,
                  batch_size: int = 10
                  ):
        assert not self.destroyed, 'find_iter could be called after destroy'
        assert self.closed, 'find_iter could not be called twice without close'

        started = self.cgi.StartFind(
            handle=self.handle,
            channel=channel,
            dirs=dirs or [],
            events=events or [],
            start_time=start_date,
            end_time=end_date,
            types=types or [],
            flags=flags or []
        )
        if not started:
            return None
        self.closed = False
        try:
            while True:
                batch = self.cgi.FindNextFile(self.handle, batch_size)
                if int(batch['found']) == 0:
                    break
                yield from batch['items']
        finally:
            self.close()

    def close(self):
        if self.handle is None:
            return
        try:
            if self.cgi.Close(self.handle):
                self.closed = True
                print('closed', self.handle, self.closed)
        except:
            pass

    def destroy(self):
        if self.destroyed:
            return
        if self.handle is None:
            return
        self.close()
        try:
            if self.cgi.Destroy(self.handle):
                self.destroyed = True
                print('destroyed', self.handle, self.destroyed)
        except:
            pass

    def __enter__(self):
        if self.handle is None:
            self.handle = self.cgi.Create()
            print('enter', self.handle)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def __repr__(self):
        return f'MediaFileFinder(handle={self.handle}, cgi={self.cgi.host})'
