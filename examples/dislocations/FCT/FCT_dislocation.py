from pathlib import Path

from pyatomsk.dislocations.builder import DislocationBuilder
from pyatomsk.dislocations.dislocation_loop import DislocationLoop
from pyatomsk.structures.atomic_structure import AtomicStructure
from pyatomsk.structures.lattices import TetragonalLattices

from voltsdk import Lattice, PluginHub

REGISTRY_URL = 'https://raw.githubusercontent.com/VoltLabs-Research/Volt/main/server/static/plugin-registry'

A = 4.0
C_OVER_A = 1.5
C = A * C_OVER_A

LAMMPS_FILE = Path('FCT_loop.lmp')
output_dir = Path('output/fct-dxa')
output_dir.mkdir(parents=True, exist_ok=True)

hub = PluginHub(url=REGISTRY_URL, default_publisher='voltlabs')
psm = hub.get('pattern-structure-matching')
dxa = hub.get('opendxa')

structure = AtomicStructure(
    lattice=TetragonalLattices.FCT,
    lattice_params=[A, C],
    species=['Ti'],
    duplicate=[12, 12, 6],
)

loop = DislocationLoop(
    x='0.501*box',
    y='0.501*box',
    z='0.501*box',
    normal='Z',
    radius=8,
    burgers=[A / 2, A / 2, 0.0],
    poisson=0.33,
)

builder = DislocationBuilder(
    atomic_structure=structure,
    input_file=None,
    output_file=str(LAMMPS_FILE),
    dislocations=[loop],
)

fct_lattice = Lattice(
    name='fct',
    matrix=True,
    coordination_number=16,
    scale=1.0,
    coordinate_mode='fractional',
    reference_basis_index=0,
    cell=[
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, C / A],
    ],
    basis=[
        [0.0, 0.0, 0.0],
        [0.0, 0.5, 0.5],
        [0.5, 0.0, 0.5],
        [0.5, 0.5, 0.0],
    ],
)

LAMMPS_FILE.unlink(missing_ok=True)
builder.generate(atomsk_output=False)

psm_run = psm(
    LAMMPS_FILE,
    output_dir=output_dir,
    lattices=fct_lattice,
)

print(psm_run['pattern_analysis'].df('main_listing'))

dxa_run = dxa(
    psm_run,
    output_dir=output_dir,
    export_as='json',
)

dislocations = dxa_run['dislocations']

print(dislocations.df('main_listing'))
print(dislocations.df('sub_listings.dislocation_segments')[['segment_id', 'burgers_vector']])
print(dislocations.path)
