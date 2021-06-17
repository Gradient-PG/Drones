"""Drone instructions definitions."""


def command() -> str:
    return "command"


def takeoff() -> str:
    return "takeoff"


def land() -> str:
    return "land"


def streamon() -> str:
    return "streamon"


def streamoff() -> str:
    return "streamoff"


def emergency() -> str:
    return "emergency"


def up(val: int) -> str:
    return f"up {val}"


def down(val: int) -> str:
    return f"down {val}"


def left(val: int) -> str:
    return f"left {val}"


def right(val: int) -> str:
    return f"right {val}"


def forward(val: int) -> str:
    return f"forward {val}"


def back(val: int) -> str:
    return f"back {val}"


def cw(val: int) -> str:
    return f"cw {val}"


def ccw(val: int) -> str:
    return f"ccw {val}"


def rc(left_right: int, fwd_back: int, up_down: int, yaw: int) -> str:
    return f"rc {left_right} {fwd_back} {up_down} {yaw}"
