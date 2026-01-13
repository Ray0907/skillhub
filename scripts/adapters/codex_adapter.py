from pathlib import Path
from .base import TargetAdapter

class CodexAdapter(TargetAdapter):
    @property
    def name(self) -> str:
        return "codex"

    @property
    def skills_dir(self) -> Path:
        return Path.home() / ".codex" / "skills"
