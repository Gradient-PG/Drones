"""Movement instruction bundle."""

from dataclasses import dataclass
from typing import List
from enum import Enum
from . import drone_instruction as di


@dataclass
class MovementInstruction:
    """Movement instruction bundle

    To translate bundle into drone's instructions, use instruction.translate()
    """

    left_right: int
    forward: int
    height: int
    yaw: int

    def translate(self) -> str:
        """Translate movement instruction to list of drone instructions"""

        return di.rc(self.left_right, self.forward, self.height, self.yaw)
