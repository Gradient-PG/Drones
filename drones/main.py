"""Main project file.

It's where the API entrypoints are accessed and used for the purpose of the project.
"""

import logging

import threading
import time

from drones.connection.connector import Connector
from common import movement_instruction as mi
import multiprocessing
import drones.image_processing as image_processing
from drones.common.processClass import ProcessClass
from drones.common.logger import setup_logger
import msvcrt


def process_communicator(connector: Connector) -> None:
    """Debug communication function to make input/commands.
    Parameters:
    ----------
    connector: Connector
        Connector to drone, which is currently used.
    """
    while True:
        if msvcrt.kbhit():
            command_to_send = msvcrt.getch()
            if command_to_send == b"s":
                connector.initialize()
                time.sleep(10)
                connector.send_instruction(mi.MovementInstruction(True, False, 0, 0, 0, 0))
                time.sleep(10)
                connector.send_instruction(mi.MovementInstruction(False, False, 50, 0, 0, 0))
                time.sleep(10)
                connector.send_instruction(mi.MovementInstruction(False, False, 0, 0, 0, 0))
            elif command_to_send == b"h":
                connector.halt()
            elif command_to_send == b"c":
                connector.close()


if __name__ == "__main__":
    connector = Connector()
    frame_queue: multiprocessing.Queue = multiprocessing.Queue()
    result_queue: multiprocessing.Queue = multiprocessing.Queue()
    image_processing_process = ProcessClass(frame_queue, result_queue)
    image_processing_process.start()

    communication_thread = threading.Thread(target=process_communicator, args=(connector,), daemon=True)
    communication_thread.start()

    while True:
        frame = connector.get_last_frame()
        if frame is not None:
            frame_queue.put(frame)
        time.sleep(0.6)
        if not result_queue.empty():
            while not result_queue.empty():
                result = result_queue.get()
                # TODO make decision
