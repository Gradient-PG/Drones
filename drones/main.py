"""Main project file.

It's where the API entrypoints are accessed and used for the purpose of the project.
"""

import logging
import threading
import time

from drones.connection.connector_template import connector
from common import movement_instruction as mi


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


i = 1


def mock():
    while True:
        global i
        connector.send_instruction(mi.MovementInstruction(i, 1, 1, 1, 1))
        i = i + 2
        time.sleep(0.1)


if __name__ == "__main__":
    setup_log()
    log = logging.getLogger()

    thr = threading.Thread(target=mock)

    while True:

        command_to_send = input("Input command: ")

        if command_to_send == "start":
            connector.initialize()
        elif command_to_send == "end":
            connector.close()
        else:
            thr.start()
