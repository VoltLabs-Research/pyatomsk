"""Friendly description of a crystal pattern for pattern-structure matching.

``Lattice`` is a small, readable wrapper around a single ``pattern_definitions``
entry consumed by the ``pattern-structure-matching`` plugin. You describe the cell
as three row vectors and the basis as fractional (or cartesian) sites, and
:meth:`Lattice.to_pattern_definition` renders the schema the plugin expects
(``cell_a``/``cell_b``/``cell_c`` + ``basis_atoms``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Union

Number = Union[int, float]
Vector3 = Sequence[Number]
BasisEntry = Union[Sequence[Number], Mapping[str, Any]]


def _vector3(value: Vector3, label: str) -> list[float]:
    components = list(value)
    if len(components) != 3:
        raise ValueError(f'{label} must have exactly 3 components, got {len(components)}.')
    return [float(component) for component in components]


def _basis_atom(entry: BasisEntry, index: int) -> dict[str, Any]:
    """Normalize a basis site to ``{'species', 'x', 'y', 'z'}``.

    Accepts ``[x, y, z]`` (species defaults to 1), ``[species, x, y, z]``, or a
    mapping with ``x``/``y``/``z`` and an optional ``species``.
    """
    if isinstance(entry, Mapping):
        if not all(axis in entry for axis in ('x', 'y', 'z')):
            raise ValueError(f"basis[{index}] mapping needs 'x', 'y' and 'z'.")
        return {
            'species': int(entry.get('species', 1)),
            'x': float(entry['x']),
            'y': float(entry['y']),
            'z': float(entry['z']),
        }

    components = list(entry)
    if len(components) == 3:
        species, position = 1, components
    elif len(components) == 4:
        species, *position = components
    else:
        raise ValueError(
            f'basis[{index}] must be [x, y, z], [species, x, y, z] or a mapping.'
        )
    return {
        'species': int(species),
        'x': float(position[0]),
        'y': float(position[1]),
        'z': float(position[2]),
    }


@dataclass
class Lattice:
    """A crystal pattern (reference topology) for pattern-structure matching.

    Example::

        Lattice(
            name='bct',
            matrix=True,
            coordination_number=14,
            cell=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.03]],
            basis=[[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
        )
    """

    name: str
    coordination_number: int
    cell: Sequence[Vector3]
    basis: Sequence[BasisEntry]
    matrix: bool = False
    scale: float = 1.0
    coordinate_mode: str = 'fractional'
    reference_basis_index: int = 0

    def to_pattern_definition(self) -> dict[str, Any]:
        """Render the ``pattern_definitions`` entry expected by the plugin."""
        cell = list(self.cell)
        if len(cell) != 3:
            raise ValueError(f"'{self.name}' cell must have exactly 3 vectors, got {len(cell)}.")
        if not self.basis:
            raise ValueError(f"'{self.name}' needs at least one basis atom.")
        return {
            'name': self.name,
            'is_matrix_phase': self.matrix,
            'coordination_number': int(self.coordination_number),
            'scale': float(self.scale),
            'coordinate_mode': self.coordinate_mode,
            'reference_basis_index': int(self.reference_basis_index),
            'cell_a': _vector3(cell[0], 'cell_a'),
            'cell_b': _vector3(cell[1], 'cell_b'),
            'cell_c': _vector3(cell[2], 'cell_c'),
            'basis_atoms': [_basis_atom(atom, index) for index, atom in enumerate(self.basis)],
        }
