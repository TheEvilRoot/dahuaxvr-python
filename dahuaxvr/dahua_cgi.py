from datetime import datetime
from typing import List, Optional

import requests

from dahuaxvr.table import TableBuilder


class DahuaCgi:

    def __init__(self, host: str, authorization):
        self.client = requests
        self.host = host
        self.authorization = authorization

    def format_time(self, time: Optional[datetime]):
        if time is None:
            return None
        return time.strftime('%Y-%-m-%-d %H:%M:%S')

    def query_array(self, name: str, array: List[str]):
        return {f'{name}[{i}]': x for i, x in enumerate(array)}

    def table_parse(self, response: requests.Response) -> dict:
        content = response.content.decode()
        t = TableBuilder()
        for line in content.splitlines():
            line = line.strip()
            if len(line) == 0:
                continue
            key, value = line.split('=')
            keys = key.split('.')
            t.push(keys, value)
        return t.build()


    def assert_response(self, response: requests.Response):
        assert response.status_code == 200, f'status code {response.status_code}\n\nResponse:\n{response.content}\n\nRequest headers:\n{response.request.headers}'
        return response

    def assert_ok(self, response: requests.Response):
        return response.content.decode().strip() == 'OK'

    def cgi_get(self, cgi: str, params: str | dict, stream: bool = False) -> requests.Response:
        return self.client.get(
            url=f'{self.host}/cgi-bin/{cgi}.cgi',
            params=params,
            auth=self.authorization,
            stream=stream
        )

    def cgi_get_action_name(self, cgi: str, action: str, name: str, **kwargs):
        return self.cgi_get(cgi, {'action': action, 'name': name, **kwargs})