from datetime import datetime
from typing import List, Optional

import requests

from dahuaxvr.table import TableBuilder

"""
Base class for all CGIs. Provides HTTP call functionality, 
response handling, parsing etc, request building helper, etc...

Requires host and authorization to construct requests.
"""


class DahuaCgi:

    """
    Initializer.
    :param host - base url of cgi server, must start with http(s):// schema
    :param authorization - any valid object or None for `requests` authorization parameter
    """
    def __init__(self, host: str, authorization):
        self.client = requests
        self.host = host
        self.authorization = authorization

    """
    Format datetime.datetime to supported by API format 2012-5-13 13:26:59
    :param time - datetime object or None
    
    Return None if `time` parameter is None, string otherwise
    """
    def format_time(self, time: Optional[datetime]):
        if time is None:
            return None
        return time.strftime('%Y-%-m-%-d %H:%M:%S')

    """
    Transform array to dict in format {key[index]: value} as API requires in query parameters
    :param name - name of array
    :param array - values of array
    
    Returns dict
    """
    def query_array(self, name: str, array: List[str]):
        return {f'{name}[{i}]': x for i, x in enumerate(array)}

    """
    Parse response as table
    :param response - requests.Response object
    
    Returns dict constructed with TableBuilder
    """
    def table_parse(self, response: requests.Response) -> dict:
        content = response.content.decode()
        return TableBuilder.parse(content)

    """
    Check response status code successfulness or raise error
    :param response - requests.Response object
    
    Returns response object when success
    """
    def assert_response(self, response: requests.Response):
        assert response.status_code == 200, f'status code {response.status_code}\n\nResponse:\n{response.content}\n\nRequest headers:\n{response.request.headers}'
        return response

    """
    Check response to be OK or ERROR
    :param response - requests.Response object
    
    Returns True when response is OK, False otherwise
    """
    def assert_ok(self, response: requests.Response):
        return response.content.decode().strip() == 'OK'

    """
    Do CGI GET request with params
    :param cgi - cgi name without .cgi extension
    :param params - query parameters or string for query
    :param stream - pass-through flag for requests.get() call
    
    Returns requests.Response object
    """
    def cgi_get(self, cgi: str, params: str | dict, stream: bool = False) -> requests.Response:
        return self.client.get(
            url=f'{self.host}/cgi-bin/{cgi}.cgi',
            params=params,
            auth=self.authorization,
            stream=stream
        )

    """
    CGI GET request with action and name parameters
    :param cgi - cgi name without .cgi extension
    :param action - action value
    :param name - name value
    
    Returns requests.Response object
    """
    def cgi_get_action_name(self, cgi: str, action: str, name: str, **kwargs):
        return self.cgi_get(cgi, {'action': action, 'name': name, **kwargs})
