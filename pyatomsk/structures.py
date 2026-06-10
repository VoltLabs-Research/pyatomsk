from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence, Union

from pyatomsk.commands import AtomskCommand, _prepare_output_path


class CubicLattices(Enum):
    SC = 'sc'
    BCC = 'bcc'
    CsCl = 'CsCl'
    FCC = 'fcc'
    L12 = 'L12'
    FLUORITE = 'fluorite'
    DIAMOND = 'diamond'
    ZINCBLENDE = 'zb'
    ROCKSALT = 'rocksalt'
    PEROVSKITE = 'per'
    A15 = 'a15'
    C15 = 'c15'


class TetragonalLattices(Enum):
    ST = 'st'
    BCT = 'bct'
    FCT = 'fct'
    L10 = 'L1_0'


class HexagonalLattices(Enum):
    HCP = 'hcp'
    WURTZITE = 'wz'
    GRAPHITE = 'graphite'
    BN = 'BN'
    B12 = 'B12'
    C14 = 'C14'
    C36 = 'C36'


Lattices = Union[CubicLattices, TetragonalLattices, HexagonalLattices]
MillerIndex = Union[str, Sequence[int]]


def _miller(index: MillerIndex) -> str:
    if isinstance(index, str):
        return index
    return '[' + ''.join(map(str, index)) + ']'


@dataclass
class AtomicStructure(AtomskCommand):
    lattice: Lattices
    lattice_params: Sequence[float]
    species: Sequence[str]
    orient: Sequence[MillerIndex] | None = None
    duplicate: Sequence[int] | None = None
    export_filename: str | None = None
    formats: Sequence[str] = ()

    def argv(self, *, include_export: bool = True) -> list[str]:
        args = ['atomsk', '--create', self.lattice.value]
        args.extend(map(str, self.lattice_params))
        args.extend(self.species)

        if self.orient is not None:
            args.append('orient')
            args.extend(_miller(index) for index in self.orient)

        if self.duplicate is not None:
            args.append('-duplicate')
            args.extend(map(str, self.duplicate))

        if include_export and self.export_filename:
            args.append(self.export_filename)
            args.extend(self.formats)

        return args

    def output_path(self) -> Path | None:
        return Path(self.export_filename) if self.export_filename else None

    def prepare_run(self) -> None:
        if self.export_filename:
            _prepare_output_path(self.export_filename)


@dataclass
class CustomAtomicStructure(AtomskCommand):
    cell: Sequence[Sequence[float]]
    basis: Sequence[tuple[str, Sequence[float]]]
    duplicate: Sequence[int] | None = None
    seed_filename: str = 'pyatomsk_seed.xsf'

    def _seed_text(self) -> str:
        lines = [
            'CRYSTAL',
            'PRIMVEC',
            *[f'{v[0]} {v[1]} {v[2]}' for v in self.cell],
            'PRIMCOORD',
            f'{len(self.basis)} 1',
        ]
        for species, frac in self.basis:
            x = frac[0] * self.cell[0][0] + frac[1] * self.cell[1][0] + frac[2] * self.cell[2][0]
            y = frac[0] * self.cell[0][1] + frac[1] * self.cell[1][1] + frac[2] * self.cell[2][1]
            z = frac[0] * self.cell[0][2] + frac[1] * self.cell[1][2] + frac[2] * self.cell[2][2]
            lines.append(f'{species} {x} {y} {z}')
        return '\n'.join(lines) + '\n'

    def write_seed(self) -> Path:
        path = Path(self.seed_filename)
        path.write_text(self._seed_text())
        return path

    def argv(self, *, include_export: bool = True) -> list[str]:
        # ``include_export`` is part of the AtomskCommand contract (so a
        # CustomAtomicStructure can be fed to DislocationBuilder), but a seed
        # command has no trailing export clause, so it is a deliberate no-op here.
        args = ['atomsk', str(Path(self.seed_filename))]
        if self.duplicate is not None:
            args.append('-duplicate')
            args.extend(map(str, self.duplicate))
        return args

    def prepare_run(self) -> None:
        self.write_seed()
