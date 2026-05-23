from dataclasses import dataclass
from typing import Sequence
from dislocations.types import Coord

@dataclass
class DislocationLoop:
    x: Coord
    y: Coord 
    z: Coord
    normal: str
    radius: float
    burgers: Sequence[float]
    poisson: float