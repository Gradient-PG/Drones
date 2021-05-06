""""""
import math
from collections import deque

from drones.common.movement_instruction import MovementInstruction
from drones.common.detection_data import DetectionData

from drones.common.drone_state import DroneState


class DecisionController:
    def __init__(self):

        self.preferred_distance: float = 100  # in cm

        self._story_size: int = 10
        self._detection_story: deque[DetectionData] = deque([], self._story_size)

    def state_process(self, detection_data: DetectionData, drone_state: DroneState) -> MovementInstruction:
        """Process state of the drone and detection data."""

        self._detection_story.append(detection_data)

        diff_x: int = 0
        diff_y: int = 0
        diff_z: int = 0
        speed: int = 0

        # Process the story of last 'self._story_size'
        if detection_data.distance < 0:
            # If distance is less than 0, it means that object was not detected on the screen
            # In such case, positions story should be reviewed to find out its expected location

            # TODO

            pass
        else:
            # If distance is greater than 0, calculate distance which needs to be covered to achieve preferred
            # distance value
            distance_d: float = self.preferred_distance - detection_data.distance

            # Then calculate the vector of movement which points to preferred position
            # TODO

            # Calculate height difference basing on pitch angle
            diff_y = int(math.sin(math.radians(detection_data.d_pitch)) * distance_d)

        return MovementInstruction(detection_data.d_yaw, diff_x, diff_y, diff_z, speed)


decision_controller = DecisionController()
