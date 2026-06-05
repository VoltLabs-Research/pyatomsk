from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Union

from voltsdk import PluginArtifact, SpatialAssembler, open_in_volt

Pathish = Union[str, os.PathLike]
Source = Union[Pathish, PluginArtifact]

_GLB_SUFFIXES = {'.glb', '.gltf'}


def _is_glb(path: Path) -> bool:
    return path.suffix.lower() in _GLB_SUFFIXES or path.name.lower().endswith('.glb.zst')


def _as_glb(source: Source, *, output_path: Pathish | None = None, **kwargs: Any) -> Path | str:
    # voltsdk artifacts already know how to convert themselves to GLB.
    if isinstance(source, PluginArtifact):
        return source.glb(output_path=output_path, **kwargs)

    path = Path(os.fspath(source))
    if _is_glb(path):
        return path

    target = Path(output_path).expanduser() if output_path else path.with_suffix('.glb')
    return SpatialAssembler().glb(path, output_path=target, **kwargs)


def view(
    source: Source | Sequence[Source],
    *,
    output_path: Pathish | None = None,
    title: str | None = None,
    volt_url: str | None = None,
    open_browser: bool = True,
    **kwargs: Any,
) -> str:
    """Open an analysis artifact, a GLB, or a path (or a list of them) in the VOLT canvas.

    Analysis files (``.json`` / ``.msgpack``) are converted to GLB via voltsdk's
    ``SpatialAssembler`` (the exporter is auto-detected from the payload); GLBs are
    passed through untouched. Compute stays local — ``voltsdk.open_in_volt`` serves the
    asset from a local http server. Returns the viewer URL.

    ``output_path`` only applies to a single source; a list uses each asset's default
    ``.glb`` path so multiple layers don't collide. Extra keyword arguments (e.g.
    ``exporter='DislocationExporter'``) are forwarded to the GLB conversion.
    """
    if isinstance(source, (str, os.PathLike, PluginArtifact)):
        glb = _as_glb(source, output_path=output_path, **kwargs)
        return open_in_volt(glb, title=title, volt_url=volt_url, open_browser=open_browser)

    frames = [_as_glb(item, **kwargs) for item in source]
    return open_in_volt(frames, title=title, volt_url=volt_url, open_browser=open_browser)
