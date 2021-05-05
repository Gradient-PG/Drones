"""Tello drone connection and communication."""

import logging
import threading
from typing import List
import configparser
import socket

from .. common.movement_instruction import MovementInstruction
from .. common.drone_state import DroneState

log = logging.getLogger()


class ConnectorTemplate:
    """Tello drone connection manager."""

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("connection/config.ini")
        config = config["NETWORK"]
        self._address_response = (config["host"], config.getint("port_response"))
        self._address_state = (config["host"], config.getint("port_state"))
        self._stream_address = config["stream_address"]
        self._tello_address = (config["tello_address"], config.getint("tello_port"))
        self._state_byte_size = config.getint("state_byte_size")
        self._response_byte_size = config.getint("response_byte_size")
        self._socket_receive_response = None
        self._socket_receive_state = None
        self._tello_connected = False
        self._response_thread: threading.Thread = None
        self._state_thread: threading.Thread = None
        self._sender_thread: threading.Thread = None
        self._last_instruction: MovementInstruction = None
        self._drone_instruction_stack: List[str] = []
        self._drone_finished_stack: List[str] = []
        self._drone_state: str = None
        self._drone_response = None

    def initialize(self) -> bool:
        """Open connection with the device and enables SDK. Start communication thread.

        Args:
            None.

        Returns:
            True if connection was established properly. False otherwise.
        """
        try:
            self._socket_receive_response = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket_receive_response.bind(self._address_response)
            self._socket_receive_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket_receive_state.bind(self._address_state)
        except (OSError, socket.herror, socket.gaierror) as err:
            log.error(f"Error {err.errno}: {err.strerror}")
        else:
            self._tello_connected = True
            self._response_thread = threading.Thread(target=self.get_response)
            self._response_thread.start()
            self._state_thread = threading.Thread(target=self.get_state)
            self._state_thread.start()
            # self.send_instruction()
            log.info("Connection established")

        return True

    def get_response(self):
        while True:
            try:
                data, server = self._socket_receive_response.recvfrom(self._response_byte_size)
                self._drone_response = data.decode(encoding="utf-8")
                log.info(f"Drone: {self._drone_response}")

            except OSError as err:
                log.error(err)
                self.close()
                break

    def send_instruction(self, instruction: MovementInstruction) -> bool:
        """Receive MovementInstruction and execute it as soon as possible.

        Args:
            instruction: MovementInstruction which is sent to drone.

        Returns:
            True if instruction was received properly by the module (not by the drone!). False otherwise.
        """

        return True

    def get_instruction(self) -> MovementInstruction:
        """Return last MovementInstruction sent to the Connector.

        Args:
            None.

        Returns:
            Last acquired movement instruction.
        """

        return self._last_instruction

    def get_state(self) -> DroneState:
        """Return last DroneState.

        Args:
            None.

        Returns:
            Last collected drone state bundle.
        """

        return DroneState(self._drone_state)

    def if_idle(self) -> bool:
        """Checks if there are any tasks queued for the module.

        Args:
            None.

        Returns:
             True if module is idle. False otherwise.
        """

        return not self._drone_instruction_stack

    def close(self) -> None:
        """Close the connection with the drone, performing the landing operation if required.

        Args:
            None.

        Returns:
            None.
        """

        if self._tello_connected:
            self._socket_receive_response.close()
            self._socket_receive_state.close()
            self._tello_connected = False
            # landing here
            log.info("Connection closed.")
        else:
            log.info("Connection is already closed")

    def halt(self) -> None:
        """Interrupt currently performed task and attempt to stop the drone quickly as it is possible.

        Args:
            None.

        Returns:
            None.
        """

        pass


