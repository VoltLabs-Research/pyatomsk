from pathlib import Path

from pyatomsk.dislocations.builder import DislocationBuilder
from pyatomsk.dislocations.dislocation_loop import DislocationLoop
from pyatomsk.structures.atomic_structure import AtomicStructure
from pyatomsk.structures.lattices import CubicLattices

from voltsdk import PluginHub

REGISTRY_URL = 'https://raw.githubusercontent.com/VoltLabs-Research/Volt/main/server/static/plugin-registry'
LAMMPS_FILE = Path('Al_loop.lmp')

output_dir = Path('output/fcc-dxa')
output_dir.mkdir(parents=True, exist_ok=True)

hub = PluginHub(url=REGISTRY_URL, default_publisher='voltlabs')
dxa = hub.get('opendxa')
ptm = hub.get('polyhedral-template-matching')

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
    poisson=0.33
)

builder = DislocationBuilder(
    atomic_structure=structure,
    input_file=None,
    output_file=str(LAMMPS_FILE),
    dislocations=[loop]
)

LAMMPS_FILE.unlink(missing_ok=True)
builder.generate()

ptm_run = ptm(
    LAMMPS_FILE,
    output_dir=output_dir,
    crystal_structure=CubicLattices.FCC.value,
    rmsd=0.1,
)

dxa_run = dxa(
    ptm_run['annotated.dump'],
    output_dir=output_dir,
    reference_topology=CubicLattices.FCC.value,
    clusters_table=ptm_run['clusters.table'],
    clusters_transitions=ptm_run['cluster_transitions.table'],
    export_as='json'
)

dislocations = dxa_run['dislocations']

print(dislocations.df("main_listing"))
print(dislocations.df("sub_listings.dislocation_segments").head())
print(dislocations.path)
