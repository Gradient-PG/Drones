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

log = logging.getLogger()


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
        config = configparser.ConfigParser()
        config.read("connection/config.ini")
        config = config["NETWORK"]
        self._address_response = (config["host"], config.getint("port_response"))
        self._address_state = (config["host"], config.getint("port_state"))
        self._tello_address = (config["tello_address"], config.getint("tello_port"))
        self._stream_address = config["stream_address"]
        self._state_byte_size = config.getint("state_byte_size")
        self._response_byte_size = config.getint("response_byte_size")
        self._socket_receive_response = None
        self._socket_receive_state = None
        self._tello_connected = False
        self._response_thread: threading.Thread = None
        self._state_thread: threading.Thread = None
        self._sender_thread: threading.Thread = None
        self._stream_thread: threading.Thread = None
        self._last_instruction: MovementInstruction = None
        self._drone_instruction_stack: List[str] = []
        self._drone_finished_stack: List[str] = []
        self._drone_state: str = None
        self._response_event = threading.Event()
        self._response_event.clear()
        self._new_instruction_event = threading.Event()
        self._drone_response: str = None
        self._drone_response_time = None

        self.frame = None
        self.should_stop: bool = False

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
            self._response_thread = threading.Thread(target=self._receive_response)
            self._response_thread.start()
            self._drone_instruction_stack.append(di.command())
            self._send_command()
            self._drone_instruction_stack.append(di.streamon())
            self._send_command()
            log.debug("Waiting for drone's response on initialize")
            if self._response_event.wait(timeout=3) and self._drone_response == "ok":
                self._tello_connected = True
                self._state_thread = threading.Thread(target=self._receive_state)
                self._state_thread.setDaemon(True)
                self._state_thread.start()
                self._sender_thread = threading.Thread(target=self._send_commands)
                self._sender_thread.setDaemon(True)
                self._sender_thread.start()
                self._stream_thread = threading.Thread(target=self._receive_frames)
                self._stream_thread.setDaemon(True)
                self._stream_thread.start()
                log.info("Connection established")
                return False
            else:
                log.info("Connecting failed")
                return True

        return True

    def _receive_response(self) -> None:
        """Receive command response UDP datagrams from Tello, log socket error, close socket on exceptions."""

        while True:
            try:
                data, server = self._socket_receive_response.recvfrom(self._response_byte_size)
                self._drone_response = data.decode(encoding="utf-8")
                self._response_event.set()
                log.info("Drone response: " + self._drone_response + "\n")

            except OSError as err:
                log.error(err)
                self.close()
                break

    def _receive_state(self) -> None:
        """Receive state UDP datagrams from Tello, log socket error, close socket on exceptions."""

        while True:
            try:
                data, server = self._socket_receive_state.recvfrom(self._state_byte_size)
                self._state = data.decode("ASCII")

            except OSError as err:
                log.error(err)
                self.close()
                break

    def _receive_frames(self) -> None:
        """Recieve stream from tello drone using OpenCv video capture. Last frame is stored in self.frame"""
        telloVideo = cv2.VideoCapture(self._stream_address)
        telloVideo.set(cv2.CAP_PROP_FPS, 3)
        while True:
            # Capture frame-by-framestreamon
            ret, frame = telloVideo.read()
            # if frame is read correctly ret is True
            if not ret:
                log.error("Can't receive frame")
                continue

            self.frame = frame

    def send_instruction(self, instruction: MovementInstruction) -> None:
        """Receive MovementInstruction and execute it as soon as possible.

        Args:
            instruction: MovementInstruction which is sent to drone.
            new_instruction_event: Event for notifying _send_command() about instruction stack change

        Returns:
            True if instruction was received properly by the module (not by the drone!). False otherwise.
        """
        self._last_instruction = instruction
        instruction_set = instruction.translate()
        self._drone_instruction_stack.clear()
        self._drone_instruction_stack.extend(instruction_set)
        self._new_instruction_event.set()

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
            # halt and land
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
        self.should_stop = True
        self._drone_instruction_stack.clear()
        self._drone_instruction_stack.append(di.land())

    def _send_commands(self):
        """Send commands to drone using command stack"""
        while True:
            if self.should_stop:
                return

            if self._tello_connected:
                if self._drone_instruction_stack:
                    self._send_command()
            else:
                log.error("Send command failed, Tello not connected!")
                break

    def _send_command(self) -> None:
        """Send one command from stack to Tello, socket must be bound."""
        # TODO "OK" to config, add timeout to config
        # TODO Add errors handling, check if Tello responds to command while doing other command
        self._response_event.clear()
        self._new_instruction_event.clear()
        command = self._drone_instruction_stack[-1]
        log.debug("Sending " + str(command))

        self._last_command = self._socket_receive_response.sendto(
            command.encode(encoding="utf-8"), self._tello_address
        )

        if "rc" not in command:
            if self._response_event.wait(timeout=10):
                if self._drone_response == "ok":
                    log.debug("Drone received: " + str(command))
                    if not self._new_instruction_event.isSet():
                        self._drone_instruction_stack.pop()
                elif "error" in self._drone_response:
                    log.debug("Unknown error, halting")
                    self.halt()
            else:
                log.debug("Drone has not received: " + str(command))
        else:
            log.debug("RC command sent")
            self._drone_instruction_stack.pop()
            # log.debug(f"Preexec state: {self._state}")
            # log.debug(f"Postexec state: {self._state}")


connector = Connector()
