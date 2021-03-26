"""Basic drone connection and communication.

Additional info.
"""

import logging


class ConnectorPrototype:
    def __init__(self):
        self.log = logging.getLogger(__name__)  # Get global logger setup

    def connect(self):
        """Sample public function, which is accessible from outside packages and is entrypoint of the library"""

        self.log.info("Connection established")
        self.log.warning("Tracking errors")

    def __track_errors(self):
        """Sample private function, which is inaccessible from outside of the package"""

        self.log.error("Sample log error")
