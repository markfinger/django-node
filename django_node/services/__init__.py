import os
import json
from ..base_service import BaseService
from ..exceptions import NodeServerConnectionError, NodeServerTimeoutError
from ..settings import SERVER_TEST_TIMEOUT


class EchoService(BaseService):
    """
    A basic service which will return the value of the parameter
    `echo` as the response.

    Internally, NodeServer uses this service to test if the server
    is running as expected.
    """

    path_to_source = os.path.join(os.path.dirname(__file__), 'echo.js')
    timeout = SERVER_TEST_TIMEOUT
    expected_output = '__NODE_SERVER_RUNNING__'

    @classmethod
    def warn_if_not_configured(cls):
        pass

    def test(self):
        self.ensure_loaded()

        try:
            response = self.get_server().send_request_to_service(
                self.get_name(),
                timeout=self.timeout,
                ensure_started=False,
                data={
                    'data': json.dumps({'echo': self.expected_output})
                }
            )
        except (NodeServerConnectionError, NodeServerTimeoutError):
            return False

        if response.status_code != 200:
            return False

        return response.text == self.expected_output