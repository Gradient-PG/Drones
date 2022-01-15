"""Tello drone connection and communication."""

import logging
import time
import datetime
import threading
from typing import List
from typing import Tuple
import configparser
import socket
import cv2
import numpy as np
from ..common.movement_instruction import MovementInstruction
from ..common import drone_instruction as di
from ..common.drone_state import DroneState
from drones.common.logger import setup_logger


class Connector:
    """Tello connection manager

    Attributes
    ----------
    address_response : (str, int)
        tuple with IP and port of host for receiving command responses from Tello
    address_state : (str, int)
        tuple with IP and port of host for receiving state from Tello
    stream_address : str
        URL to Tello string
    tello_address : (str, int)
        tuple with IP and port of Tello for sending commands
    socket_receive_response : socket
        socket for receiving Tello responses
    socket_receive_state : socket
        socket for receiving Tello state
    tello_connected : bool
        connection flag
    response_receiving_thread : Thread
        thread handling receiving Tello responses
    state_receiving_thread : Thread
        thread handling receiving Tello state
    state : str
        last received Tello state
    response : str
        last received Tello response
    last_command : str
        last sent command

    Methods
    -------
    connect()
        Binds host sockets, creates data receiving Threads and starts them. Enables SKD on Tello.
    disconnect()
        Closes sockets.
    receive_response()
        Receive command response UDP datagrams from Tello, log socket error, close socket on exceptions.
    receive_state()
        Receive state UDP datagrams from Tello, log socket error, close socket on exceptions.
    send_command(command: str)
        Sends command to Tello
    """

    def __init__(self):
        self._should_stop = False
        config = configparser.ConfigParser()
        config.read("connection/config.ini")
        config = config["NETWORK"]
        self.log = setup_logger("main_log", "logfile.log")
        self._address_response = (config["host"], config.getint("port_response"))
        self._address_state = (config["host"], config.getint("port_state"))
        self._tello_address = (config["tello_address"], config.getint("tello_port"))
        self.stream_address = config["stream_address"]
        self._state_byte_size = config.getint("state_byte_size")
        self._response_byte_size = config.getint("response_byte_size")
        self._init_attempts = config.getint("init_attempts")
        self._response_timeout = config.getint("response_timeout")
        self._socket_receive_response = None
        self._socket_receive_state = None
        self._tello_connected = False
        self._response_thread: threading.Thread = None
        self._state_thread: threading.Thread = None
        self._sender_thread: threading.Thread = None
        self._stream_thread: threading.Thread = None
        self._last_instruction: MovementInstruction = None

        self._landed: bool = True
        self.is_stream_on: bool = False

        self._current_rc: str = di.rc(0, 0, 0, 0)
        self._send_takeoff: bool = False
        self._send_land: bool = False
        self._send_stream_on: bool = False
        self._send_stream_off: bool = False

        self._drone_state: str = None
        self._response_event = threading.Event()
        self._response_event.clear()
        self._new_instruction_event = threading.Event()
        self._drone_response: str = None
        self._drone_response_time = None

        self.should_stop: bool = False

    def initialize(self) -> bool:
        """Open connection with the device and enables SDK. Start communication thread.

        Args:
            None.

        Returns:
            True if connection was established properly. False otherwise.
        """

        try:
            # Initialize and bind sockets for receiving drone's responses and state
            self._socket_receive_response = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket_receive_response.bind(self._address_response)
            self._socket_receive_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket_receive_state.bind(self._address_state)
        except (OSError, socket.herror, socket.gaierror) as err:
            self.log.error(f"Error {err.errno}: {err.strerror}")
        # If no exceptions thrown
        else:
            # Initialize response receiving thread and send SDK initialization command
            self._response_thread = threading.Thread(target=self._receive_response)
            self._response_thread.start()

            # Try to establish connection 5 times
            for tries in range(1, self._init_attempts + 1):
                self.log.debug("Waiting for drone's response on initialize. Attempt " + str(tries) + ".")
                if self._send_command(di.command()):
                    # Set connection flag and initialize threads for receiving state, stream and sending commands
                    self._tello_connected = True
                    self._state_thread = threading.Thread(target=self._receive_state, daemon=True)
                    self._state_thread.start()
                    self._sender_thread = threading.Thread(target=self._send_commands, daemon=True)
                    self._sender_thread.start()
                    self.log.info("Connection established")
                    return True

        self.log.info("Connecting failed")
        return False

    def _receive_response(self) -> None:
        """Receive command response UDP datagrams from Tello, log socket error, close socket on exceptions."""

        while True:
            try:
                data, server = self._socket_receive_response.recvfrom(self._response_byte_size)
                self._drone_response = data.decode(encoding="utf-8")
                self._response_event.set()
                self.log.info("Drone response: " + self._drone_response + "\n")

            except OSError as err:
                self.log.error(err)
                self.close()
                break

    def _receive_state(self) -> None:
        """Receive state UDP datagrams from Tello, log socket error, close socket on exceptions."""

        while True:
            try:
                data, server = self._socket_receive_state.recvfrom(self._state_byte_size)
                self._state = data.decode("ASCII")

            except OSError as err:
                self.log.error(err)
                self.close()
                break

    def send_instruction(self, instruction: MovementInstruction) -> bool:
        """Receive MovementInstruction and execute it as soon as possible.

        Args:
            instruction: MovementInstruction which is sent to drone.

        Returns:
            True if instruction was received properly by the module (not by the drone!). False otherwise.
        """

        if not self._should_stop:
            self._last_instruction = instruction
            self._current_rc = instruction.translate()
            return True
        return False

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

        return DroneState(self._state)

    def if_idle(self) -> bool:
        """Checks if there are any tasks queued for the module.

        Args:
            None.

        Returns:
             True if module is idle. False otherwise.
        """

        return not (self._send_stream_off or self._send_stream_on or self._send_land or self._send_takeoff)

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
            self.log.info("Connection closed.")
        else:
            self.log.info("Connection is already closed")

    def halt(self) -> None:
        """Interrupt currently performed task and attempt to stop the drone quickly as it is possible.

        Args:
            None.

        Returns:
            None.
        """
        self._should_stop = True
        self._current_rc = di.rc(0, 0, 0, 0)
        self._send_land = True
        self._send_takeoff = False
        self._send_stream_off = False
        self._send_stream_on = False
        return

    def _send_commands(self):
        """Sends current RC and takeoff, land, streamon, streamoff commands until drone is disconnected.

        Args:
            None.

        Returns:
            None.
        """

        while True:
            if self._tello_connected:

                self._send_rc()
                time.sleep(0.5)

                # If land command should be sent
                if self._send_land and self._send_command(di.land()):
                    # If sending land is successful set landed flag
                    self._landed = True
                    self._send_land = False

                # If drone is not halting
                if not self._should_stop:
                    # If takeoff command should be sent
                    if self._send_takeoff and self._send_command(di.takeoff()):
                        # If sending takeoff is successful reset landed flag
                        self._landed = False
                        self._send_takeoff = False

                    # If streamon command should be sent
                    if self._send_stream_on and self._send_command(di.streamon()):
                        # If sending streamon is successful set stream_on flag
                        self.is_stream_on = True
                        self._send_stream_on = False

                    # If streamoff command should be sent
                    if self._send_stream_off and self._send_command(di.streamoff()):
                        # If sending streamoff is successful reset stream_on flag
                        self.is_stream_on = False
                        self._send_stream_off = False

            else:
                self.log.error("Send command failed, Tello not connected!")
                break

    def takeoff(self) -> None:
        """Instruct drone to takeoff"""
        if not self._should_stop:
            self._send_takeoff = True

    def land(self) -> None:
        """Instruct drone to land"""
        if not self._should_stop:
            self._send_land = True

    def stream_on(self) -> None:
        """Instruct drone to turn on stream"""
        if not self._should_stop:
            self._send_stream_on = True

    def stream_off(self) -> None:
        """Instruct drone to turn off stream"""
        if not self._should_stop:
            self._send_stream_off = True

    def _send_command(self, command: str) -> bool:
        """Send command to tello, socket must be bound."""

        self._response_event.clear()

        self.log.debug("Sending " + str(command))
        self._socket_receive_response.sendto(command.encode(encoding="utf-8"), self._tello_address)

        if self._response_event.wait(timeout=self._response_timeout):
            if self._drone_response == "ok":
                self.log.debug("Drone received: " + str(command))
                return True
            elif "error" in self._drone_response:
                self.log.debug("Unknown error, halting")
        else:
            self.log.debug("Drone has not responded within timeout: " + str(command))

        return False

    def _send_rc(self) -> None:
        """Send RC command to tello, socket must be bound."""
        rc = self._current_rc
        self._socket_receive_response.sendto(rc.encode(encoding="utf-8"), self._tello_address)
        self.log.debug("Sent " + str(rc))
