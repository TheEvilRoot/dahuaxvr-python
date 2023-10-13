from dahuaxvr.dahua_cgi import DahuaCgi


class ConfigManagerCgi(DahuaCgi):

    def GetConfig(self, name: str, **kwargs):
        return self.table_parse(self.assert_response(self.cgi_get_action_name('configManager', 'getConfig', name, **kwargs)))

    def GetRTSPConfig(self):
        return self.GetConfig('RTSP')
