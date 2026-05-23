from dataclasses import dataclass, field
from typing import Sequence

from pyatomsk.commands import AtomskCommand
from pyatomsk.dislocations.dislocation import Dislocation
from pyatomsk.dislocations.dislocation_loop import DislocationLoop
from pyatomsk.structures.atomic_structure import AtomicStructure


@dataclass
class DislocationBuilder(AtomskCommand):
    atomic_structure: AtomicStructure
    input_file: str | None
    output_file: str | None
    formats: Sequence[str] = ()
    dislocations: list[Dislocation | DislocationLoop] = field(default_factory=list)
    options: list[str] = field(default_factory=list)

    def to_command(self) -> str:
        commands = [
            self.atomic_structure.to_command(include_export=self.output_file is None)
        ]

        for dislocation in self.dislocations:
            commands.append(dislocation.to_command())

        if self.options:
            commands.append(' '.join(self.options))

        if self.output_file:
            commands.append(' '.join([ self.output_file, *self.formats ]))

        return ' '.join(commands)
