from pathlib import Path

from pyatomsk import (
    AtomicStructure,
    CubicLattices,
    DislocationBuilder,
    DislocationLoop,
    PluginHub,
    view,
)

LAMMPS_FILE = Path('Al_loop.lmp')
OUTPUT_DIR = Path('output/fcc-dxa')

hub = PluginHub(default_publisher='voltlabs')
ptm = hub.get('polyhedral-template-matching')
dxa = hub.get('opendxa')

structure = AtomicStructure(
    lattice=CubicLattices.FCC,
    lattice_params=[4.06],
    species=['Al'],
    orient=['[110]', '[1-12]', '[-111]'],
    duplicate=[60, 40, 20],
)
loop = DislocationLoop(
    x='0.501*box',
    y='0.501*box',
    z='0.501*box',
    normal='Z',
    radius=30,
    burgers=[2.860954, 0, 0],
    poisson=0.33,
)
builder = DislocationBuilder(
    atomic_structure=structure,
    output_file=str(LAMMPS_FILE),
    dislocations=[loop],
)
builder.run()

ptm_run = ptm(
    LAMMPS_FILE,
    output_dir=OUTPUT_DIR,
    crystal_structure=CubicLattices.FCC,
    rmsd=0.1,
)
dxa_run = dxa(
    ptm_run,
    output_dir=OUTPUT_DIR,
    reference_topology=CubicLattices.FCC,
)

print(dxa_run['dislocations'].df('main_listing'))

view(ptm_run['atoms'], output_path=OUTPUT_DIR / 'ptm_atoms.glb')
view(dxa_run['dislocations'])
