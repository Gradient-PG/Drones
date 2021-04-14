"""Movement instruction bundle
"""

from dataclasses import dataclass
from typing import List

import drone_instruction as di


@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class MovementInstruction:
    """Movement instruction bundle

    To translate bundle into drone's instructions, use instruction.translate()
    """

    target_yaw: int
    diff_x: int
    diff_y: int
    diff_z: int
    speed: int

    def translate(self) -> List[str]:
        """Translate movement instruction to list of drone instructions"""

        return [di.command(), di.takeoff(), di.land()]
