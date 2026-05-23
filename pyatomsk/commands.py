from __future__ import annotations

import shlex
import subprocess
from typing import Any


class AtomskCommand:
    def to_command(self) -> str:
        raise NotImplementedError

    def generate(
        self,
        *,
        check: bool = True,
        text: bool = True,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            shlex.split(self.to_command()),
            check=check,
            text=text,
            **kwargs,
        )
