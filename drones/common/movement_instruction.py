"""Movement instruction bundle."""

from dataclasses import dataclass
from typing import List
from typing import Tuple

from . import drone_instruction as di


@dataclass
class MovementInstruction:
    """Movement instruction bundle

    To translate bundle into drone's instructions, use instruction.translate()
    """

    target_yaw: int
    diff_x: int
    diff_y: int
    diff_z: int
    speed: int

    def translate(self) -> List[Tuple[str, int]]:
        """Translate movement instruction to list of drone instructions"""

        return [(di.command(), self.target_yaw + 1), (di.command(), self.target_yaw)]
