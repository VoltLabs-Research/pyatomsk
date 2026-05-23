from dataclasses import dataclass, field
from typing import Sequence, Union

from structures.atomic_structure import AtomicStructure
from dislocations.dislocation import Dislocation
from dislocations.dislocation_loop import DislocationLoop


@dataclass
class DislocationBuilder:
    atomic_structure: AtomicStructure
    input_file: str | None
    output_file: str | None
    formats: Sequence[str] = ()
    dislocations: list[Dislocation | DislocationLoop] = field(default_factory=list)
    options: list[str] = field(default_factory=list)

    def to_command(self) -> str:
        commands = [self.atomic_structure.to_command()]

        for dislocation in self.dislocations:
            commands.append(dislocation.to_command())

        if self.options:
            commands.append(' '.join(self.options))

        if self.output_file:
            commands.append(' '.join([ self.output_file, *self.formats ]))

        return ' '.join(commands)