from pyatomsk.structures.atomic_structure import AtomicStructure
from pyatomsk.structures.lattices import CubicLattices
from pyatomsk.dislocations.builder import DislocationBuilder
from pyatomsk.dislocations.dislocation_loop import DislocationLoop

structure = AtomicStructure(
    lattice=CubicLattices.FCC,
    lattice_params=[4.06],
    species=['Al'],
    orient=['[110]', '[1-12]', '[-111]'],
    duplicate=[60, 40, 20],
    export_filename='Al_supercell.xsf'
)

loop = DislocationLoop(
    x='0.501*box',
    y='0.501*box',
    z='0.501*box',
    normal='Z',
    radius=30,
    burgers=[2.860954, 0, 0],
    poisson=0.33
)

builder = DislocationBuilder(
    atomic_structure=structure,
    input_file='Al_supercell.xsf',
    export_file='Al_loop.cfg',
    dislocations=[loop]
)

builder.t