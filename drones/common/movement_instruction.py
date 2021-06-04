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

    # speed: int

    def translate(self) -> List[str]:
        """Translate movement instruction to list of drone instructions"""

        sequence: List[str] = []

        # if self.takeoff:
        #    sequence.append(di.takeoff())

        # if self.target_yaw > 0:
        #     sequence.append(di.cw(self.target_yaw))
        # elif self.target_yaw < 0:
        #     sequence.append(di.cw(-self.target_yaw))

        # sequence.append(di.rc(0, 0, 0, 100))
        # sequence.append(di.rc(0, 0, 0, -100))
        # sequence.append(di.rc(0, 0, 0, 0))

        # if self.diff_fwd > 0:
        #     sequence.append(di.forward(self.diff_fwd))
        # elif self.diff_fwd < 0:
        #     sequence.append(di.back(-self.diff_fwd))
        #
        # if self.diff_rl > 0:
        #     sequence.append(di.right(self.diff_rl))
        # elif self.diff_rl < 0:
        #     sequence.append(di.left(-self.diff_rl))
        #
        # if self.diff_y > 0:
        #     sequence.append(di.up(self.diff_y))
        # elif self.diff_y < 0:
        #     sequence.append(di.down(-self.diff_y))

        # if self.land:
        #    sequence.append(di.land())

        sequence.reverse()

        return sequence
        # return [(di.command(), self.target_yaw + 1), (di.command(), self.target_yaw)]
