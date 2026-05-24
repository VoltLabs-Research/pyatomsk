import shlex
import subprocess
from typing import Any


class AtomskCommand:
    def to_command(self) -> str:
        raise NotImplementedError

    def generate(
        self,
        atomsk_output: bool = False,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        run_kwargs = dict(kwargs)

        if not atomsk_output:
            run_kwargs['stderr'] = subprocess.PIPE
            run_kwargs['stdout'] = subprocess.PIPE

        return subprocess.run(
            shlex.split(self.to_command()),
            check=True,
            text=True,
            **run_kwargs
        )
