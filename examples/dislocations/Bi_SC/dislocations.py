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
    crystal_structure=CubicLattices.SC,
    rmsd=0.1,
)

dxa_run = dxa(
    ptm_run,
    output_dir=OUTPUT_DIR,
    reference_topology=CubicLattices.SC,
)

dislocations = dxa_run['dislocations']

print(dislocations.df('main_listing'))

segments = dislocations.df('export.DislocationExporter.segments')
print(segments[['segment_id', 'burgers_vector', 'magnitude', 'length']].to_string(index=False))

view(dislocations, output_path=OUTPUT_DIR / 'dislocations.glb')
