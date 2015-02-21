import os
from .base_service import BaseService
from .exceptions import NodeServerConnectionError, NodeServerTimeoutError
from .settings import SERVER_TEST_TIMEOUT


class EchoService(BaseService):
    path_to_source = os.path.join(os.path.dirname(__file__), 'services', 'echo.js')
    timeout = SERVER_TEST_TIMEOUT
    expected_output = '__NODE_SERVER_RUNNING__'

    def test(self):
        try:
            response = self.get_server().get_service(
                self.get_name(),
                timeout=self.timeout,
                ensure_started=False,
                params={
                    'echo': self.expected_output
                }
            )
        except (NodeServerConnectionError, NodeServerTimeoutError):
            return False

        if response.status_code != 200:
            return False

        return response.text == self.expected_output