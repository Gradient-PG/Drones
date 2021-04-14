"""Tello drone connection and communication.

Additional info.
"""

import logging
import threading
from typing import List

from ..common.movement_instruction import MovementInstruction
from ..common.drone_state import DroneState

log = logging.getLogger()


class ConnectorTemplate:
    """Tello drone connection manager
    TODO:
    """

    _response_thread: threading.Thread
    _sender_thread: threading.Thread
    _last_instruction: MovementInstruction
    _drone_instruction_stack: List[str]
    _drone_finished_stack: List[str]
    _drone_state: str

    def __init__(self):
        self._drone_instruction_stack = []
        self._drone_finished_stack = []

    def initialize(self) -> bool:
        """Opens connection with the device and enables SDK. Starts communication thread."""

        return True

    def send_instruction(self, instruction: MovementInstruction) -> bool:
        """Receives MovementInstruction and executes it as soon as possible."""

        return True

    def get_instruction(self) -> MovementInstruction:
        """Returns last MovementInstruction sent to the Connector."""

        return self._last_instruction

    def get_state(self) -> DroneState:
        """Returns last DroneState."""

        return DroneState(self._drone_state)

    def if_idle(self) -> bool:
        """Returns true if drone is idle and doesn't have any instructions queued."""

        return True if not self._drone_instruction_stack else False

    def close(self) -> None:
        """Closes the connection with the drone, performing the landing operation if required."""

        return

    def halt(self) -> None:
        """Interrupts currently performed task and attempts to stop the drone quickly as it is possible."""

        return


connector = ConnectorTemplate()
