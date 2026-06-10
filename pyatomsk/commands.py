import shlex
import subprocess
from pathlib import Path
from typing import Any


class AtomskError(RuntimeError):
    """Raised when the ``atomsk`` subprocess exits with a non-zero status.

    Carries the executed ``command``, the ``returncode`` and the captured
    ``stderr`` so failures are debuggable without re-running by hand.
    """

    def __init__(self, command: list[str], returncode: int, stderr: str) -> None:
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        message = f'atomsk failed (exit {returncode}).\n$ {shlex.join(command)}'
        detail = (stderr or '').strip()
        if detail:
            message += f'\n{detail}'
        super().__init__(message)


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

    def argv(self, *, include_export: bool = True) -> list[str]:
        raise NotImplementedError

    def to_command(self, *, include_export: bool = True) -> str:
        return shlex.join(self.argv(include_export=include_export))

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
        """Run the command and return :meth:`output_path` (``None`` if it only prints).

        On a non-zero exit (and ``check=True``, the default) raises
        :class:`AtomskError` with the captured stderr included in the message.
        """
        from pyatomsk.atomsk import ensure_atomsk

        run_kwargs = dict(kwargs)
        if not atomsk_output:
            run_kwargs.setdefault('stdout', subprocess.PIPE)
            run_kwargs.setdefault('stderr', subprocess.PIPE)
        self.prepare_run()
        argv = self.argv()
        argv[0] = str(ensure_atomsk())
        completed = subprocess.run(argv, check=False, text=text, **run_kwargs)
        if check and completed.returncode != 0:
            stderr = completed.stderr if isinstance(completed.stderr, str) else ''
            raise AtomskError(argv, completed.returncode, stderr)
        return self.output_path()
