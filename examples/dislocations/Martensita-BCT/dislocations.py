from pathlib import Path

from pyatomsk import (
    AtomicStructure,
    Dislocation,
    DislocationBuilder,
    DislocationCharacter,
    Lattice,
    PluginHub,
    TetragonalLattices,
    view,
)

REGISTRY_URL = 'https://raw.githubusercontent.com/VoltLabs-Research/Volt/main/server/static/plugin-registry'
LAMMPS_FILE = Path('BCT_martensite_edge_add.lmp')
OUTPUT_DIR = Path('output/bct-martensite-dxa')

A = 2.86
C_OVER_A = 1.03
C = A * C_OVER_A

hub = PluginHub(url=REGISTRY_URL, default_publisher='voltlabs')
psm = hub.get('pattern-structure-matching')
dxa = hub.get('opendxa')

# BCT martensite with an extra-half-plane (edge_add) dislocation.
structure = AtomicStructure(
    lattice=TetragonalLattices.BCT,
    lattice_params=[A, C],
    species=['Fe'],
    duplicate=[32, 32, 24],
)
edge = Dislocation(
    character=DislocationCharacter.EDGE_ADD,
    p1='0.501*box',
    p2='0.501*box',
    line='z',
    plane='y',
    burgers=[A],
    poisson=0.29,
)
builder = DislocationBuilder(
    atomic_structure=structure,
    output_file=str(LAMMPS_FILE),
    dislocations=[edge],
)
builder.run()

# Custom BCT pattern for pattern-structure-matching.
bct_lattice = Lattice(
    name='bct',
    matrix=True,
    coordination_number=14,
    scale=1.0,
    coordinate_mode='fractional',
    reference_basis_index=0,
    cell=[
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, C_OVER_A],
    ],
    basis=[
        [0.0, 0.0, 0.0],
        [0.5, 0.5, 0.5],
    ],
)

# PSM carries runtime lattices, so DXA auto-wires lattice_dir + reference_topology
# (and the cluster tables) directly from psm_run.
psm_run = psm(LAMMPS_FILE, output_dir=OUTPUT_DIR, lattices=[bct_lattice])
dxa_run = dxa(psm_run, output_dir=OUTPUT_DIR, export_as='json')

print(dxa_run['dislocations.json'].df())

# View the extracted dislocations and the defect mesh in VOLT as separate scenes.
# (PSM emits per-atom data without an atomistic exporter, so the renderable
# artifacts here are DXA's dislocation lines and defect mesh.)
view(dxa_run['dislocations.json'], output_path=OUTPUT_DIR / 'dislocations.glb')
view(dxa_run['defect_mesh.json'], output_path=OUTPUT_DIR / 'defect_mesh.glb')

