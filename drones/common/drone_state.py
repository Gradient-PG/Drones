"""Drone state bundle."""

from dataclasses import dataclass
import re


@dataclass(init=False)
class DroneState:
    """Drone state bundle."""

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
        """
        Translate given state string to state variables.
        :param state_str: specified string with all state data
        """

        state_list = re.findall(r"(\d+)(\.\d+)*", state_str)

        self.pitch = int(state_list[0])
        self.roll = int(state_list[1])
        self.yaw = int(state_list[2])
        self.vgx = int(state_list[3])
        self.vgy = int(state_list[4])
        self.vgz = int(state_list[5])
        self.templ = int(state_list[6])
        self.temph = int(state_list[7])
        self.tof = int(state_list[8])
        self.h = int(state_list[9])
        self.bat = int(state_list[10])
        self.baro = float(state_list[11])
        self.time = int(state_list[12])
        self.agx = float(state_list[13])
        self.agy = float(state_list[14])
        self.agz = float(state_list[15])
