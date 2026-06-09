from pathlib import Path

from pyatomsk import (
    CubicLattices,
    PluginHub,
    view,
)

HERE = Path(__file__).resolve().parent
LAMMPS_FILE = HERE / 'timestep-1275000.dump'
OUTPUT_DIR = HERE / 'output' / 'bi-sc-dxa'

hub = PluginHub(default_publisher='voltlabs')
ptm = hub.get('polyhedral-template-matching')
dxa = hub.get('opendxa')

ptm_run = ptm(
    LAMMPS_FILE,
    output_dir=OUTPUT_DIR,
    crystal_structure=CubicLattices.SC.value,
    rmsd=0.1,
    logs=True,
)

dxa_run = dxa(
    ptm_run['annotated.dump'],
    output_dir=OUTPUT_DIR,
    clusters_table=ptm_run['clusters.table'],
    clusters_transitions=ptm_run['cluster_transitions.table'],
    lattice_dir=dxa.root / 'share' / 'volt' / 'lattices',
    reference_topology=CubicLattices.SC.value,
    logs=True,
)

dislocations = dxa_run['dislocations.msgpack']

# Network summary.
print(dislocations.df('main_listing'))

# Burgers vector of each extracted dislocation segment.
segments = dislocations.df('export.DislocationExporter.segments')
print(segments[['segment_id', 'burgers_vector', 'magnitude', 'length']].to_string(index=False))

view(dislocations, output_path=OUTPUT_DIR / 'dislocations.glb')
