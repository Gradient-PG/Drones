"""Basic drone connection and communication.

Additional info.
"""
import threading
import socket
import sys
import time
import logging

log = logging.getLogger()


class Connector:
    def __init__(self):
        self.address_response = ('', 9000)  # Tello sends command responses on port 9000
        self.address_state = ('', 8890)  # Tello sends state on port 9000
        self.stream_address = "udp://" + "0.0.0.0" + ':' + "11111"  # Stream link
        self.tello_address = ('192.168.10.1', 8889)
        self.socket_response = None  # Socket for response receiving and command sending
        self.socket_state = None  # Socket for state receiving
        self.tello_connected = False  # Connection flag
        self.response_receiving_thread = None
        self.state_receiving_thread = None
        self.state = None
        self.response = None

    def connect(self):
        """Establish connection to Tello and enable SDK."""

        self.socket_response = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_response.bind(self.address_response)
        self.socket_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_state.bind(self.address_state)
        self.tello_connected = True
        self.response_receiving_thread = threading.Thread(target=self.receive_response)
        self.response_receiving_thread.start()
        self.state_receiving_thread = threading.Thread(target=self.receive_state)
        self.state_receiving_thread.start()
        self.send_command("command");

        log.info("Connection established.")

    def disconnect(self):
        self.socket_response.close()
        self.socket_state.close()
        log.info("Connection closed.")

    def receive_response(self):
        """Receive command response UDP datagrams from Tello, log socket error, close socket on exceptions."""

        while True:
            try:
                data, server = self.socket_response.recvfrom(1518)
                self.response = data.decode(encoding="utf-8")
                log.info(self.response + "\n")

            except socket.error as err:
                log.error(err)
                break

        self.tello_connected = False

    def receive_state(self):
        """Receive state UDP datagrams from Tello, log socket error, close socket on exceptions."""

        while True:
            try:
                data, server = self.socket_state.recvfrom(1024)
                self.state = data.decode('ASCII')

            except socket.error as err:
                log.error(err)
                break

        self.tello_connected = False

    def receive_stream(self):
        # TODO
        return None

    def send_command(self, command):
        """Send specified command to Tello, socket must be bound."""

        if self.tello_connected:
            if command:
                command = command.encode(encoding="utf-8")
                sent = self.socket_response.sendto(command, self.tello_address)
            else:
                log.error("Command empty!")
        else:
            log.error("Tello not connected!")


connector = Connector()
