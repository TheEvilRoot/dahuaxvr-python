from dahuaxvr.dahua_cgi import DahuaCgi


class ConfigManagerCgi(DahuaCgi):

    def GetConfig(self, name: str, **kwargs):
        return self.table_parse(self.assert_response(self.cgi_get_action_name('configManager', 'getConfig', name, **kwargs)))

    def SetConfig(self, name: str, **kwargs):
        return self.assert_ok(self.assert_response(self.cgi_get_action_name('configManager', 'setConfig', name, **kwargs)))

    def GetRTSPConfig(self):
        return self.GetConfig('RTSP')

    def GetVideoOutConfig(self):
        return self.GetConfig('VideoOut')

    def GetVideoEncodeConfig(self):
        return self.GetConfig('Encode')

