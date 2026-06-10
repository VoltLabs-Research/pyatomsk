# Python wrapper for Atomsk

## Install

```bash
pip install pyatomsk
```

## Quick start

```python
from pathlib import Path
from pyatomsk import AtomicStructure, CubicLattices, DislocationBuilder, DislocationLoop, PluginHub, view

OUT = Path('output/fcc-dxa')

hub = PluginHub(default_publisher='voltlabs')   # uses registry.voltcloud.dev by default
ptm = hub.get('polyhedral-template-matching')
dxa = hub.get('opendxa')

# 1. Build an FCC Al slab with a prismatic dislocation loop.
structure = AtomicStructure(
    lattice=CubicLattices.FCC,
    lattice_params=[4.06],
    species=['Al'],
    orient=['[110]', '[1-12]', '[-111]'],
    duplicate=[60, 40, 20],
)
loop = DislocationLoop(x='0.501*box', y='0.501*box', z='0.501*box',
                       normal='Z', radius=30, burgers=[2.860954, 0, 0], poisson=0.33)
builder = DislocationBuilder(atomic_structure=structure, output_file='Al_loop.lmp', dislocations=[loop])
lmp = builder.run()                      # downloads Atomsk if needed, returns the output Path

# 2. Run the analysis plugins locally. DXA consumes PTM's annotated dump and tables.
ptm_run = ptm(lmp, output_dir=OUT, crystal_structure='fcc', rmsd=0.1)
dxa_run = dxa(
    ptm_run['annotated.dump'],
    output_dir=OUT,
    clusters_table=ptm_run['clusters.table'],
    clusters_transitions=ptm_run['cluster_transitions.table'],
    reference_topology='fcc',
    export_as='json',
)

# 3. Inspect results as a DataFrame, then view them in VOLT.
print(dxa_run['dislocations.json'].df())
view(ptm_run['atoms.msgpack'], output_path=OUT / 'ptm_atoms.glb')
view(dxa_run['dislocations.json'])
```


## Building structures

`AtomicStructure` maps directly onto `atomsk --create`. You can inspect the command
before running it:

```python
from pyatomsk import AtomicStructure, CubicLattices

s = AtomicStructure(
    lattice=CubicLattices.FCC,
    lattice_params=[4.05],          # a (and c for tetragonal/hexagonal)
    species=['Al'],
    duplicate=[10, 10, 10],
    export_filename='al.xsf',
    formats=['xsf'],
)
s.to_command()   # 'atomsk --create fcc 4.05 Al -duplicate 10 10 10 al.xsf xsf'
s.run()          # executes it, returns Path('al.xsf')
```

Lattice enums: `CubicLattices` (FCC, BCC, SC, diamond, …), `TetragonalLattices`
(BCT, FCT, ST, L1_0) and `HexagonalLattices` (HCP, graphite, …).

For non-standard cells, `CustomAtomicStructure` writes an XSF seed from an explicit
`cell` + fractional `basis` and feeds it to Atomsk.

## Adding dislocations

`DislocationBuilder` prepends a structure command and appends one or more
`-dislocation` fragments:

```python
from pyatomsk import AtomicStructure, TetragonalLattices, Dislocation, DislocationCharacter, DislocationBuilder

structure = AtomicStructure(lattice=TetragonalLattices.BCT, lattice_params=[2.86, 2.95],
                            species=['Fe'], duplicate=[32, 32, 24])
edge = Dislocation(character=DislocationCharacter.EDGE_ADD, p1='0.501*box', p2='0.501*box',
                   line='z', plane='y', burgers=[2.86], poisson=0.29)

builder = DislocationBuilder(atomic_structure=structure, output_file='bct.lmp', dislocations=[edge])
builder.run()
```

Use `DislocationLoop` for prismatic loops (`-dislocation loop …`). Both are pure
command fragments; only `DislocationBuilder` (and the structures) are runnable.


## Running VOLT plugins 

Plugins are fetched from a VOLT plugin registry and executed as local subprocesses by
voltsdk. A `PluginRun` exposes its outputs as artifacts you
can look up by name (fuzzy: `.json` ⇄ `.msgpack`, prefixes stripped):

```python
run = ptm(lmp, output_dir='out', crystal_structure='fcc', rmsd=0.1)
run['annotated.dump']          # PluginArtifact (os.PathLike)
run['clusters.table'].df()     # pandas DataFrame
run['atoms.msgpack'].json()    # parsed payload
```

Artifacts are `os.PathLike`, so you wire one plugin's outputs into the next by passing them
explicitly. OpenDXA takes the annotated dump as its input plus the PTM/PSM cluster tables:

```python
dxa_run = dxa(
    ptm_run['annotated.dump'],
    output_dir='out',
    clusters_table=ptm_run['clusters.table'],
    clusters_transitions=ptm_run['cluster_transitions.table'],
    reference_topology='fcc',
)
```

After a `pattern-structure-matching` run, read `lattice_dir` and `reference_topology` from the
PSM manifest (`psm_run['pattern_structure_matching_manifest.json'].json()`) and pass them to
`dxa(...)` — see `examples/dislocations/Martensita-BCT/`.

## Viewing in VOLT

`view()` converts an artifact (or a path / list of them) to GLB, the exporter is detected
from the payload, and opens it in the VOLT canvas via a local server. GLB files pass
through untouched.

```python
view(dxa_run['dislocations.json'])                              # opens in VOLT
view(ptm_run['atoms.msgpack'], output_path='atoms.glb')         # also keep the GLB
view(dxa_run['defect_mesh.json'], exporter='MeshExporter')      # force a specific layer
```

`view()` returns the viewer URL. Equivalent low-level voltsdk calls are re-exported too:
`PluginArtifact.glb()`, `PluginArtifact.open_in_volt()`, and `open_in_volt(path)`.

## Configuration

| Variable | Purpose |
|---|---|
| `ATOMSK_BIN` | Path to an existing Atomsk executable (skips auto-download). |
| `XDG_CACHE_HOME` | Cache root; Atomsk under `<cache>/pyatomsk`, plugins under `<cache>/volt`. |
| `VOLT_PLUGIN_REGISTRY` | Override the plugin registry URL. |
| `VOLT_CACHE_DIR` | Override the voltsdk (plugin) cache directory. |
| `VOLT_APP_URL` | VOLT app URL used by the viewer. |

## API reference

| Symbol | Description |
|---|---|
| `AtomicStructure`, `CustomAtomicStructure` | Build a crystal via `atomsk --create` / an XSF seed. |
| `CubicLattices`, `TetragonalLattices`, `HexagonalLattices` | Lattice type enums. |
| `Dislocation`, `DislocationLoop` | `-dislocation` command fragments. |
| `DislocationBuilder` | Combine a structure with one or more dislocations. |
| `AtomskCommand` | Base class: `.argv()`, `.to_command()`, `.run() -> Path \| None`. |
| `AtomskError` | Raised when the `atomsk` subprocess exits non-zero (carries `command`, `returncode`, `stderr`). |
| `view(source, *, output_path=None, …)` | Open an artifact/GLB/list in the VOLT canvas. |
| `PluginHub`, `Plugin`, `PluginRun`, `PluginArtifact`, `SpatialAssembler`, `open_in_volt` | Re-exported from voltsdk. |

## License

See the repository for license details.
