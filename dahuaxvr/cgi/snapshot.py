from io import BytesIO

import PIL.Image

from dahuaxvr.dahua_cgi import DahuaCgi

class SnapshotCgi(DahuaCgi):
    def GetSnapshot(self, channel: int):
        response = self.assert_response(self.cgi_get('snapshot', {'channel': str(channel)}))
        return PIL.Image.open(BytesIO(response.content))
