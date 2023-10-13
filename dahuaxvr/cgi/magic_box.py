from dahuaxvr.dahua_cgi import DahuaCgi


class MagicBoxCgi(DahuaCgi):

    def __init__(self, host: str, authorization):
        super().__init__(host, authorization)

    def GetMaxExtraStreamCounts(self):
        response = self.assert_response(self.cgi_get_action_name('magicBox', 'getProductDefinition', 'MaxExtraStream'))
        table = self.table_parse(response)
        return table['table.MaxExtraStream']
