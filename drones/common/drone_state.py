"""Drone state bundle
"""

from dataclasses import dataclass


@dataclass(init=False, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class DroneState:
    """Drone state bundle

    To create, state string is required.
    """

    pitch: int
    roll: int
    yaw: int
    vgx: int
    vgy: int
    vgz: int
    templ: int
    temph: int
    tof: int
    h: int
    bat: int
    baro: float
    time: int
    agx: float
    agy: float
    agz: float

    def __init__(self, state_str: str):
        # TODO: translate state_str to attributes values
        self.pitch = 0
