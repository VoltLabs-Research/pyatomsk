import shlex
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Sequence, Union

from pyatomsk.commands import AtomskCommand, _prepare_output_path

Coord = Union[int, float, str]
Burgers = Union[float, Sequence[float]]


class DislocationCharacter(Enum):
    EDGE = 'edge'
    EDGE_ADD = 'edge_add'
    EDGE_RM = 'edge_rm'
    SCREW = 'screw'
    MIXED = 'mixed'
    LOOP = 'loop'


def _burgers_args(burgers: Burgers) -> list[Coord]:
    if isinstance(burgers, Sequence) and not isinstance(burgers, (str, bytes)):
        return list(burgers)
    return [burgers]


class DislocationSpec:
    """An ``-dislocation ...`` argv fragment (not a standalone command)."""

    def argv(self) -> list[str]:
        raise NotImplementedError

    def to_command(self) -> str:
        return shlex.join(self.argv())


@dataclass
class Dislocation(DislocationSpec):
    character: DislocationCharacter
    p1: Coord
    p2: Coord
    line: str
    plane: str
    burgers: Burgers
    poisson: float | None = None

    def argv(self) -> list[str]:
        args = [
            '-dislocation',
            self.p1,
            self.p2,
            self.character.value,
            self.line,
            self.plane,
            *_burgers_args(self.burgers),
        ]
        if self.poisson is not None:
            args.append(self.poisson)
        return [str(arg) for arg in args]


@dataclass
class DislocationLoop(DislocationSpec):
    x: Coord
    y: Coord
    z: Coord
    normal: str
    radius: float
    burgers: Sequence[float]
    poisson: float

    def argv(self) -> list[str]:
        args = [
            '-dislocation',
            'loop',
            self.x,
            self.y,
            self.z,
            self.normal,
            self.radius,
            *self.burgers,
            self.poisson,
        ]
        return [str(arg) for arg in args]


@dataclass
class DislocationBuilder(AtomskCommand):
    atomic_structure: AtomskCommand
    output_file: str | None = None
    formats: Sequence[str] = ()
    dislocations: list[DislocationSpec] = field(default_factory=list)
    options: list[str] = field(default_factory=list)

    def argv(self, *, include_export: bool = True) -> list[str]:
        command = list(self.atomic_structure.argv(include_export=self.output_file is None))

        for dislocation in self.dislocations:
            command.extend(dislocation.argv())

        if self.options:
            command.extend(self.options)

        if include_export and self.output_file:
            command.append(self.output_file)
            command.extend(self.formats)

        return command

    def output_path(self) -> Path | None:
        return Path(self.output_file) if self.output_file else None

    def prepare_run(self) -> None:
        self.atomic_structure.prepare_run()
        if self.output_file:
            _prepare_output_path(self.output_file)
