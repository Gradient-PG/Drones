"""Tello drone connection and communication."""

import logging
import threading
from typing import List

from ..common.movement_instruction import MovementInstruction
from ..common.drone_state import DroneState

log = logging.getLogger()


class ConnectorTemplate:
    """Tello drone connection manager."""

    def __init__(self):
        self._response_thread: threading.Thread = None
        self._sender_thread: threading.Thread = None
        self._last_instruction: MovementInstruction = None
        self._drone_instruction_stack: List[str] = []
        self._drone_finished_stack: List[str] = []
        self._drone_state: str = None

    def initialize(self) -> bool:
        """Open connection with the device and enables SDK. Start communication thread.

        Args:
            None.

        Returns:
            True if connection was established properly. False otherwise.
        """

        return True

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

        pass

    def halt(self) -> None:
        """Interrupt currently performed task and attempt to stop the drone quickly as it is possible.

        Args:
            None.

        Returns:
            None.
        """

        pass


connector = ConnectorTemplate()
