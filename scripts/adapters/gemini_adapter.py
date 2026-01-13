from pathlib import Path
from .base import TargetAdapter

class GeminiAdapter(TargetAdapter):
    @property
    def name(self) -> str:
        return "gemini"

    @property
    def skills_dir(self) -> Path:
        return Path.home() / ".gemini" / "skills"
