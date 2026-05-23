from dataclasses import dataclass
from typing import Sequence, Union

from pyatomsk.pyatomsk.structures.lattices import CubicLattices, TetragonalLattices, HexagonalLattices

MillerIndex = Union[str, Sequence[int]]

@dataclass
class AtomicStructure:
    lattice: Union[CubicLattices, TetragonalLattices, HexagonalLattices]
    lattice_params: Sequence[float]
    species: Sequence[str]
    orient: Sequence[MillerIndex] | None = None
    duplicate: Sequence[int] | None = None
    export_filename: str | None = None
    formats: Sequence[str] = ()

    def to_command(self) -> str:
        args = ['atomsk', '--create', self.lattice.value]
        args.extend(map(str, self.lattice_params))
        args.extend(self.species)

        if self.orient is not None:
            args.append('orient')
            args.extend(_miller(index) for index in self.orient)

        if self.duplicate is not None:
            args.append('-duplicate')
            args.extend(map(str, self.duplicate))

        if self.export_filename:
            args.append(self.export_filename)
            args.extend(self.formats)

        return ' '.join(args)


def _miller(index: MillerIndex) -> str:
    if isinstance(index, str):
        return index
    return '[' + ''.join(map(str, index)) + ']'
