from datetime import datetime
from typing import List, Optional
from requests.utils import requote_uri
from dahuaxvr.dahua_cgi import DahuaCgi


class MediaFileFindCgi(DahuaCgi):

    def FindNextFile(self, handle,
                     count: int):
        response = self.assert_response(self.cgi_get('mediaFileFind', {'action': 'findNextFile', 'object': str(handle), 'count': count}))
        table = self.table_parse(response)
        return table


    def StartFind(self, handle,
                  channel: int,
                  dirs: List[str],
                  events: List[str],
                  start_time: Optional[datetime],
                  end_time: Optional[datetime],
                  types: List[str],
                  flags: List[str]):
        params = {
            'action': 'findFile',
            'object': str(handle),
            'condition.Channel': str(channel),
            'condition.StartTime': self.format_time(start_time),
            'condition.EndTime': self.format_time(end_time),
            **self.query_array('condition.Types', types),
            **self.query_array('condition.Flag', flags),
            **self.query_array('condition.Events', events),
            **self.query_array('condition.Dirs', dirs)
        }
        params = '&'.join([f'{key}={requote_uri(value)}' for key, value in params.items() if value is not None])
        response = self.assert_response(self.cgi_get('mediaFileFind', params))
        print(response.content)
        return response.content.decode().strip() == 'OK'

    def Create(self):
        response = self.assert_response(self.cgi_get('mediaFileFind', {'action': 'factory.create'}))
        table = self.table_parse(response)
        return table['result']

    def Close(self, handle):
        response = self.assert_response(self.cgi_get('mediaFileFind', {'action': 'close', 'object': handle}))
        return response.content.decode().strip() == 'OK'

    def Destroy(self, handle):
        response = self.assert_response(self.cgi_get('mediaFileFind', {'action': 'destroy', 'object': handle}))
        return response.content.decode().strip() == 'OK'
