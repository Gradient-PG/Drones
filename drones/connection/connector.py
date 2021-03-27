"""Basic drone connection and communication.

Additional info.
"""

import threading
import socket
import logging
import configparser

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
        self.address_response = (config["host"], config.getint("port_response"))
        self.address_state = (config["host"], config.getint("port_state"))
        self.stream_address = config["stream_address"]
        self.tello_address = (config["tello_address"], config.getint("tello_port"))
        self.state_byte_size = config.getint("state_byte_size")
        self.response_byte_size = config.getint("response_byte_size")
        self.socket_receive_response = None
        self.socket_receive_state = None
        self.tello_connected = False
        self.response_receiving_thread = None
        self.state_receiving_thread = None
        self.state = None
        self.response = None
        self.last_command = None

    def connect(self) -> None:
        """Establish connection to Tello and enable SDK."""

        try:
            self.socket_receive_response = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_receive_response.bind(self.address_response)
            self.socket_receive_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_receive_state.bind(self.address_state)
        except (OSError, socket.herror, socket.gaierror) as err:
            log.error(f"Error {err.errno}: {err.strerror}")
        else:
            self.tello_connected = True
            self.response_receiving_thread = threading.Thread(target=self.receive_response)
            self.response_receiving_thread.start()
            self.state_receiving_thread = threading.Thread(target=self.receive_state)
            self.state_receiving_thread.start()
            self.send_command("command")
            log.info("Connection established.")

    def disconnect(self) -> None:
        """Close sockets"""

        if self.tello_connected:
            self.socket_receive_response.close()
            self.socket_receive_state.close()
            self.tello_connected = False
            log.info("Connection closed.")
        else:
            log.info("Connection is closed already.")

    def receive_response(self) -> None:
        """Receive command response UDP datagrams from Tello, log socket error, close socket on exceptions."""

        # TODO
        # Await response with timeout

        while True:
            try:
                data, server = self.socket_receive_response.recvfrom(self.response_byte_size)
                self.response = data.decode(encoding="utf-8")
                log.info(self.response + "\n")

            except OSError as err:
                log.error(err)
                self.disconnect()
                break

    def receive_state(self) -> None:
        """Receive state UDP datagrams from Tello, log socket error, close socket on exceptions."""

        while True:
            try:
                data, server = self.socket_receive_state.recvfrom(self.state_byte_size)
                self.state = data.decode("ASCII")

            except OSError as err:
                log.error(err)
                self.disconnect()
                break

    def send_command(self, command: str) -> None:
        """Send specified command to Tello, socket must be bound."""

        if self.tello_connected:
            if command:
                self.last_command = self.socket_receive_response.sendto(
                    command.encode(encoding="utf-8"), self.tello_address
                )
            else:
                log.warning("Command empty!")
        else:
            log.error("Tello not connected!")


connector = Connector()
