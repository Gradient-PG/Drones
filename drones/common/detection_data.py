"""Data determined and wrapped by image-processing module."""

from dataclasses import dataclass
from drone_state import DroneState


@dataclass
class DetectionData:
    """Drone state bundle."""

    distance: float
    d_yaw: int
    d_pitch: int

    drone_state: DroneState
