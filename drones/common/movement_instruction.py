"""Movement instruction bundle."""

from dataclasses import dataclass
from typing import List, Tuple

from . import drone_instruction as di


@dataclass
class MovementInstruction:
    """Movement instruction bundle

    To translate bundle into drone's instructions, use instruction.translate()
    """

    takeoff: bool
    land: bool
    target_yaw: int
    diff_fwd: int
    diff_rl: int
    diff_y: int

    def translate(self) -> List[str]:
        """Translate movement instruction to list of drone instructions"""

        sequence: List[str] = []

        if self.takeoff:
            sequence.append(di.takeoff())

        sequence.append(di.rc(self.diff_rl, self.diff_fwd, self.diff_y, self.target_yaw))

        if self.land:
            sequence.append(di.land())

        sequence.reverse()

        return sequence
