from dahuaxvr.dahua_cgi import DahuaCgi


class EncodeCgi(DahuaCgi):

    def GetVideoConfigCaps(self, params: dict):
        response = self.assert_response(self.cgi_get('encode', {'action': 'getConfigCaps', **params}))
        return self.table_parse(response)