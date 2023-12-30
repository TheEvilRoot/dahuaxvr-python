from dahuaxvr.dahua_cgi import DahuaCgi


class LoadFileCgi(DahuaCgi):
    def __init__(self, host: str, authorization):
        super().__init__(host, authorization)

    def load_file(self, file_path: str):
        response = self.client.get(
            url=f'{self.host}/cgi-bin/RPC_Loadfile/{file_path}',
            auth=self.authorization
        )
        response = self.assert_response(response)
        print(file_path, len(response.content), 'bytes')
        return response.content
