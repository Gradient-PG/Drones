"""Drone state bundle."""

from dataclasses import dataclass


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
        state_list = state_str.split(";")

        self.pitch = int(state_list[0].split(":")[1])
        self.roll = int(state_list[1].split(":")[1])
        self.yaw = int(state_list[2].split(":")[1])
        self.vgx = int(state_list[3].split(":")[1])
        self.vgy = int(state_list[4].split(":")[1])
        self.vgz = int(state_list[5].split(":")[1])
        self.templ = int(state_list[6].split(":")[1])
        self.temph = int(state_list[7].split(":")[1])
        self.tof = int(state_list[8].split(":")[1])
        self.h = int(state_list[9].split(":")[1])
        self.bat = int(state_list[10].split(":")[1])
        self.baro = float(state_list[11].split(":")[1])
        self.time = int(state_list[12].split(":")[1])
        self.agx = float(state_list[13].split(":")[1])
        self.agy = float(state_list[14].split(":")[1])
        self.agz = float(state_list[15].split(":")[1])
