"""Main project file.

It's where the API entrypoints are accessed and used for the purpose of the project.
"""

import logging
import threading
import time

from drones.connection.connector import connector
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


if __name__ == "__main__":
    setup_log()
    log = logging.getLogger()

    while True:

        command_to_send = input("Input command: ")
        started = False

        if command_to_send == "start":
            connector.initialize()
            # connector.send_instruction(mi.MovementInstruction(True, True, 90, 100, -50, -20))
        elif command_to_send == "end":
            connector.close()
        elif command_to_send == "s":
            connector.halt()
