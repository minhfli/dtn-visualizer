from dataclasses import dataclass, field


@dataclass
class Area:
    width: float
    height: float


@dataclass
class Node:
    nid: str
    type: str
    group: int
    color: tuple
    buffer_size: int
    ranges: list = field(default_factory=list)

    pos: tuple = (0.0, 0.0)
    buffer: list = field(default_factory=list)
    route: list = field(default_factory=list)


@dataclass
class Event:
    type: str
    data: dict


@dataclass
class TimeFrame:
    time: float
    events: list[Event]
