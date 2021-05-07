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
