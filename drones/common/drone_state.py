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

        self.pitch = int(state_list[0][0])
        self.roll = int(state_list[1][0])
        self.yaw = int(state_list[2][0])
        self.vgx = int(state_list[3][0])
        self.vgy = int(state_list[4][0])
        self.vgz = int(state_list[5][0])
        self.templ = int(state_list[6][0])
        self.temph = int(state_list[7][0])
        self.tof = int(state_list[8][0])
        self.h = int(state_list[9][0])
        self.bat = int(state_list[10][0])
        self.baro = float(state_list[11][0])
        self.time = int(state_list[12][0])
        self.agx = float(state_list[13][0])
        self.agy = float(state_list[14][0])
        self.agz = float(state_list[15][0])
