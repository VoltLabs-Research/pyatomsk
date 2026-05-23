from enum import Enum
from dataclasses import dataclass
from typing import Union, Sequence

Coord = Union[int, float, str]


class DislocationCharacter(Enum):
    EDGE = 'edge'
    EDGE_ADD = 'edge_add'
    EDGE_RM = 'edge_rm'
    SCRE = 'screw'
    MIXED = 'mixed'
    LOOP = 'loop'


@dataclass
class DislocationBuilder:
    character: Union[DislocationBuilder, str]
    coords: tuple[Coord, Coord] | None
    line_direction: str | None
    plane_normal: str | None
    burgers: float | Sequence[float] | None
    poisson: float | None
    loop_center: tuple[Coord, Coord, Coord] | None
    loop_normal: str | None
    loop_radius: float | None
    atomic_structure: AtomicStructure | None 
    input_file: str | None
    output_file: str | None
    formats: Sequence[str] | None

    def _dislocation_args(self) -> list[str]:
        args = ['-dislocation']
        
        if self.character == DislocationCharacter.LOOP:
            args.extend([
                self.character,
                *self.loop_center,
                self.loop_normal,
                *self.burgers,
                self.poisson
            ])

            return args

        args.extend([self.character, self.line_direction, self.plane_normal, self.burgers])

        if self.character in {DislocationCharacter.EDGE_ADD, DislocationCharacter.EDGE, DislocationCharacter.EDGE_RM}:
            args.append(self.poisson)

        return args

    def to_command(self, formats: Sequence[str] | None = None) -> str:
        args = ['atomsk', self.input_file]
        args.extend(self._dislocation_args())
        args.append(self.output_file)
        args.extend(formats)
        return args