from typing import List

from dahuaxvr.cgi.media_file_find import MediaFileFindCgi


class MediaFileFinder:
    def __init__(self, cgi: MediaFileFindCgi,
                 ):
        self.cgi = cgi
        self.handle = None
        self.closed = False
        self.destroyed = False

    def next(self):
        pass

    def close(self):
        if self.closed:
            return
        if self.handle is None:
            return
        try:
            if self.cgi.Close(self.handle):
                self.closed = True
                print(self.closed)
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
                print(self.destroyed)
        except:
            pass

    def __enter__(self):
        if self.handle is None:
            self.handle = self.cgi.Create()
            print(self.handle)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def __repr__(self):
        return f'MediaFileFinder(handle={self.handle}, cgi={self.cgi.host})'


