import shlex
import subprocess
from pathlib import Path
from typing import Any


def _prepare_output_path(path: str | Path) -> Path:
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.is_dir():
            raise IsADirectoryError(f'Expected a file output path, got directory: {target}')
        target.unlink()
    return target


class AtomskCommand:
    """Base for objects that generate (and run) an ``atomsk`` command."""

    def argv(self) -> list[str]:
        raise NotImplementedError

    def to_command(self) -> str:
        return shlex.join(self.argv())

    def prepare_run(self) -> None:
        """Hook for filesystem prep (seed files, output paths). Default: no-op."""

    def output_path(self) -> Path | None:
        """Path the command writes, or ``None`` if it only prints to stdout."""
        return None

    def run(
        self,
        *,
        atomsk_output: bool = False,
        check: bool = True,
        text: bool = True,
        **kwargs: Any,
    ) -> Path | None:
        from pyatomsk.atomsk import ensure_atomsk

        run_kwargs = dict(kwargs)
        if not atomsk_output:
            run_kwargs.setdefault('stdout', subprocess.PIPE)
            run_kwargs.setdefault('stderr', subprocess.PIPE)
        self.prepare_run()
        argv = self.argv()
        argv[0] = str(ensure_atomsk())
        subprocess.run(argv, check=check, text=text, **run_kwargs)
        return self.output_path()
