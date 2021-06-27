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
from drones.common.image_processor import ImageProcessor
from drones.common.logger import setup_logger
from drones.common.KBHit import KBHit
from drones.common.frame_getter import FrameGetterProcess


def process_communicator(connector: Connector) -> None:
    """Debug communication function to make input/commands.
    Parameters:
    ----------
    connector: Connector
        Connector to drone, which is currently used.
    """
    kbhit = KBHit()
    flag = 0
    while True:
        if kbhit.kbhit():
            command_to_send = kbhit.getch()
            if command_to_send == "s" and flag == 0:
                flag = 1
                connector.initialize()
                connector.takeoff()
                connector.stream_on()
            elif command_to_send == "h":
                connector.halt()
            elif command_to_send == "c":
                connector.close()


if __name__ == "__main__":
    connector = Connector()
    frame_queue: multiprocessing.Queue = multiprocessing.Queue()
    result_queue: multiprocessing.Queue = multiprocessing.Queue()
    image_processing_process = ImageProcessor(frame_queue, result_queue, True)
    image_processing_process.start()

    frame_getter_process = FrameGetterProcess(frame_queue, connector.stream_address)
    frame_getter_process.start()

    communication_thread = threading.Thread(target=process_communicator, args=(connector,), daemon=True)
    communication_thread.start()
    it = 0
    while True:
        if not result_queue.empty():
            result = result_queue.get()
            width, height, distance = 0, 0, 0
            it = it + 1
            connector.log.info(str(result) + str(it))
            if len(result) > 0:
                result_width, result_height, result_distance = result[0]
                if result_width > 15:
                    width = 20
                elif result_width < -15:
                    width = -20
                if result_height > 15:
                    height = -20
                elif result_height < -15:
                    height = 20
                if result_distance > 200:
                    distance = 20
            connector.send_instruction(mi.MovementInstruction(0, distance, height, width))
