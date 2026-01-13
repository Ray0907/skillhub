from pathlib import Path
from .base import TargetAdapter

class ClaudeAdapter(TargetAdapter):
    @property
    def name(self) -> str:
        return "claude"

    @property
    def skills_dir(self) -> Path:
        return Path.home() / ".claude" / "skills"
