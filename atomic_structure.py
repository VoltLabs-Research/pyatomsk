from dataclasses import dataclass
from typing import Union, Sequence
from lattices import CubicLattices, TetragonalLattices, HexagonalLattices

MillerIndex = Union[str, Sequence[int]]

@dataclass
class AtomicStructure:
    lattice: Union[CubicLattices, TetragonalLattices, HexagonalLattices]
    lattice_params: Sequence[float]
    species: Sequence[str]

    orient: Sequence[MillerIndex] | None
    duplicate: Sequence[int] | None
    export_filename: str | None 
    formats: Sequence[str] | None

    def to_command(self, formats: Sequence[str] | None = None) -> str:
        args = ['atomsk', '--create', self.lattice.value, self.lattice_params, self.species]

        if self.orient is not None:
            args.append('orient', self.orient)
        
        if self.duplicate is not None:
            args.extend('duplicate', self.duplicate)

        if self.export_filename:
            args.append(self.export_filename, formats)

        return ' '.join(args)
        