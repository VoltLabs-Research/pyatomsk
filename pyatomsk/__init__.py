"""Build Atomsk structures/dislocations, run plugins locally, and view results in VOLT.

Plugin compute runs on your machine via :mod:`voltsdk`; visualization is delegated to the
VOLT canvas (``view`` / ``open_in_volt``). pyatomsk's own surface is just the Atomsk command
builders plus a thin viewer helper.
"""

from voltsdk import (
    Plugin,
    PluginArtifact,
    PluginError,
    PluginHub,
    PluginRun,
    SpatialAssembler,
    open_in_volt,
)

from pyatomsk.commands import AtomskCommand
from pyatomsk.dislocations import (
    Dislocation,
    DislocationBuilder,
    DislocationCharacter,
    DislocationLoop,
)
from pyatomsk.patterns import Lattice
from pyatomsk.structures import (
    AtomicStructure,
    CubicLattices,
    CustomAtomicStructure,
    HexagonalLattices,
    TetragonalLattices,
)
from pyatomsk.view import view

__all__ = [
    # voltsdk re-exports (local compute, VOLT viewing)
    'PluginHub',
    'Plugin',
    'PluginArtifact',
    'PluginRun',
    'PluginError',
    'SpatialAssembler',
    'open_in_volt',
    # Atomsk command builders
    'AtomskCommand',
    'AtomicStructure',
    'CustomAtomicStructure',
    'CubicLattices',
    'TetragonalLattices',
    'HexagonalLattices',
    'Lattice',
    'Dislocation',
    'DislocationCharacter',
    'DislocationLoop',
    'DislocationBuilder',
    # thin viewer helper
    'view',
]
