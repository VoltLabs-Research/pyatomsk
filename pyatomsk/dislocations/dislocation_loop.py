from dataclasses import dataclass
from typing import Sequence

from pyatomsk.dislocations.types import Coord


@dataclass
class DislocationLoop:
    x: Coord
    y: Coord 
    z: Coord
    normal: str
    radius: float
    burgers: Sequence[float]
    poisson: float

    def to_command(self) -> str:
        args = [
            '-dislocation',
            'loop',
            self.x,
            self.y,
            self.z,
            self.normal,
            self.radius,
            *self.burgers,
            self.poisson
        ]

        return ' '.join(map(str, args))
