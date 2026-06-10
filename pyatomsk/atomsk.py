"""Resolve the Atomsk executable, downloading the official binary if needed."""

from __future__ import annotations

import os
import platform
import shutil
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ATOMSK_VERSION = 'b0.13.1'
_BASE_URL = 'https://atomsk.univ-lille.fr/code'

# (system, machine) -> (archive filename, executable name)
_BINARIES = {
    ('linux', 'x86_64'): (f'atomsk_{ATOMSK_VERSION}_Linux-amd64.tar.gz', 'atomsk'),
    ('linux', 'amd64'): (f'atomsk_{ATOMSK_VERSION}_Linux-amd64.tar.gz', 'atomsk'),
    ('linux', 'i686'): (f'atomsk_{ATOMSK_VERSION}_Linux-i686.tar.gz', 'atomsk'),
    ('linux', 'i386'): (f'atomsk_{ATOMSK_VERSION}_Linux-i686.tar.gz', 'atomsk'),
    ('windows', 'amd64'): (f'atomsk_{ATOMSK_VERSION}_Windows.zip', 'atomsk.exe'),
    ('windows', 'x86_64'): (f'atomsk_{ATOMSK_VERSION}_Windows.zip', 'atomsk.exe'),
}


def _cache_dir() -> Path:
    base = os.environ.get('XDG_CACHE_HOME') or str(Path.home() / '.cache')
    return Path(base) / 'pyatomsk'


def _extract(archive: Path, target: Path) -> None:
    if archive.name.endswith('.tar.gz'):
        with tarfile.open(archive, 'r:gz') as tar:
            # ``filter='data'`` (Python 3.12+) rejects unsafe members; older
            # interpreters fall back to the historical behaviour.
            if hasattr(tarfile, 'data_filter'):
                tar.extractall(target, filter='data')
            else:
                tar.extractall(target)
    elif archive.suffix == '.zip':
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target)
    else:
        raise ValueError(f'Unsupported Atomsk archive: {archive.name}')


def ensure_atomsk(*, version: str = ATOMSK_VERSION, force: bool = False) -> Path:
    """Return the Atomsk executable for this OS, downloading and caching it if needed.

    Resolution order: ``$ATOMSK_BIN`` -> ``atomsk`` on PATH -> cached download ->
    download the official binary. Only Linux and Windows on x86 have official static
    binaries; elsewhere (macOS, ARM) install Atomsk yourself (e.g.
    ``conda install -c conda-forge atomsk``) and point ``ATOMSK_BIN`` at it or add it
    to PATH.
    """
    override = os.environ.get('ATOMSK_BIN')
    if override:
        return Path(override).expanduser()

    if not force:
        on_path = shutil.which('atomsk')
        if on_path:
            return Path(on_path)

    system, machine = platform.system().lower(), platform.machine().lower()
    entry = _BINARIES.get((system, machine))
    if entry is None:
        raise RuntimeError(
            f'No prebuilt Atomsk binary for {system}-{machine}. Install it '
            '(e.g. `conda install -c conda-forge atomsk`), add it to PATH, or set '
            'ATOMSK_BIN to its location. See https://atomsk.univ-lille.fr/dl.php'
        )

    filename, exe = entry
    install_dir = _cache_dir() / 'atomsk' / version / f'{system}-{machine}'
    if install_dir.is_dir() and not force:
        cached = next(install_dir.rglob(exe), None)
        if cached is not None:
            return cached

    downloads = _cache_dir() / 'downloads'
    downloads.mkdir(parents=True, exist_ok=True)
    archive = downloads / filename
    if not archive.is_file() or force:
        with urllib.request.urlopen(f'{_BASE_URL}/{filename}') as response, archive.open('wb') as out:
            shutil.copyfileobj(response, out)

    if install_dir.exists():
        shutil.rmtree(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    _extract(archive, install_dir)

    binary = next(install_dir.rglob(exe), None)
    if binary is None:
        raise RuntimeError(f'{exe!r} not found inside the downloaded Atomsk archive {filename!r}.')
    binary.chmod(binary.stat().st_mode | 0o111)
    return binary
