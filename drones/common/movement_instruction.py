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

    rcA: int
    rcB: int
    rcC: int
    rcD: int

    def translate(self) -> str:
        """Translate movement instruction to list of drone instructions"""

        return di.rc(self.rcA, self.rcB, self.rcC, self.rcD)
