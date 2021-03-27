"""Main project file.

It's where the API entrypoints are accessed and used for the purpose of the project.
"""

import logging
from drones.connection import connector


def setup_log() -> None:
    """Setup global log config."""

    fh = logging.FileHandler("logfile.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(filename)s] [%(levelname)s] : %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logging.basicConfig(level=logging.DEBUG, handlers=[fh, ch])
    logging.info("Log initialized")


if __name__ == "__main__":
    setup_log()
    log = logging.getLogger()

    while True:

        command_to_send = input("Input command: ")

        if command_to_send == "start":
            connector.connect()
        elif connector.tello_connected:
            if command_to_send == "end":
                connector.disconnect()
            else:
                connector.send_command(command_to_send)
