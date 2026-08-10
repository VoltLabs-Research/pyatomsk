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

LAMMPS_FILE = Path('BCT_martensite_edge_add.lmp')
OUTPUT_DIR = Path('output/bct-martensite-dxa')

A = 2.86
C_OVER_A = 1.03
C = A * C_OVER_A

hub = PluginHub(default_publisher='voltlabs')
psm = hub.get('pattern-structure-matching')
dxa = hub.get('opendxa')

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

DislocationBuilder(
    atomic_structure=structure,
    output_file=str(LAMMPS_FILE),
    dislocations=[edge],
).run()

bct = Lattice(
    name='bct',
    coordination_number=14,
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

psm_run = psm(LAMMPS_FILE, output_dir=OUTPUT_DIR, pattern_definitions=[bct.to_pattern_definition()])
manifest = psm_run['pattern_structure_matching_manifest.json'].json()

dxa_run = dxa(
    psm_run,
    output_dir=OUTPUT_DIR,
    lattice_dir=manifest['opendxa_lattice_dir'],
    reference_topology=manifest['reference_topology'],
)

dislocations = dxa_run['dislocations']

print(dislocations.df('main_listing'))

segments = dislocations.df('export.DislocationExporter.segments')
print(segments[['segment_id', 'burgers_vector', 'magnitude', 'length']].to_string(index=False))


view(dxa_run['dislocations'], output_path=OUTPUT_DIR / 'dislocations.glb')
view(dxa_run['defect_mesh'], output_path=OUTPUT_DIR / 'defect_mesh.glb')