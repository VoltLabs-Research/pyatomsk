from pathlib import Path

from pyatomsk import (
    AtomicStructure,
    CubicLattices,
    DislocationBuilder,
    DislocationLoop,
    PluginHub,
    view,
)

REGISTRY_URL = 'https://raw.githubusercontent.com/VoltLabs-Research/Volt/main/server/static/plugin-registry'
LAMMPS_FILE = Path('Al_loop.lmp')
OUTPUT_DIR = Path('output/fcc-dxa')

hub = PluginHub(url=REGISTRY_URL, default_publisher='voltlabs')
ptm = hub.get('polyhedral-template-matching')
dxa = hub.get('opendxa')

# Build an FCC Al slab with a prismatic dislocation loop via Atomsk.
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

# Local plugin compute: PTM classifies the structure, then DXA extracts dislocations.
ptm_run = ptm(
    LAMMPS_FILE,
    output_dir=OUTPUT_DIR,
    crystal_structure=CubicLattices.FCC.value,
    rmsd=0.1,
)
# PTM runs do not carry runtime lattices, so reference_topology stays explicit;
# the annotated dump and cluster tables are auto-wired from ptm_run.
dxa_run = dxa(
    ptm_run,
    output_dir=OUTPUT_DIR,
    reference_topology=CubicLattices.FCC.value,
    export_as='json',
)

print(dxa_run['dislocations.json'].df())

# View the results in VOLT (compute stays local; the viewer is a local http server).
view(ptm_run['atoms.msgpack'], output_path=OUTPUT_DIR / 'ptm_atoms.glb')
view(dxa_run['dislocations.json'])
