from dataclasses import dataclass
from dislocations.types import Burgers, Coord
from enum import Enum

class DislocationCharacter(Enum):
    EDGE = 'edge'
    EDGE_ADD = 'edge_add'
    EDGE_RM = 'edge_rm'
    SCREW = 'screw'
    MIXED = 'mixed'
    LOOP = 'loop'
    

@dataclass
class Dislocation:
    character: DislocationCharacter
    p1: Coord
    p2: Coord
    line: str
    plane: str
    burgers: Burgers
    poisson: float | None

    def to_command(self) -> str:
        args = ['-dislocation', self.p1, self.p2, self.character.value, self.line, self.plane, *self.burgers]
        if self.poisson is not None:
            args.append(self.poisson)

        return ' '.join(map(str, args))
    