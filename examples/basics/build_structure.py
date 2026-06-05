"""Build a crystal with Atomsk — the minimal pyatomsk workflow.

Mirrors the "Building structures" snippet in the README. Atomsk is downloaded
automatically on first use, so there is nothing to install by hand.
"""

from pyatomsk import AtomicStructure, CubicLattices

structure = AtomicStructure(
    lattice=CubicLattices.FCC,
    lattice_params=[4.05],          # a (add c for tetragonal / hexagonal lattices)
    species=['Al'],
    duplicate=[10, 10, 10],
    export_filename='al.xsf',
    formats=['xsf'],
)

# Inspect the exact atomsk command without running it.
print(structure.to_command())
# 'atomsk --create fcc 4.05 Al -duplicate 10 10 10 al.xsf xsf'

# Run it (downloads atomsk if needed); returns the produced Path.
path = structure.run()
print('wrote', path)
