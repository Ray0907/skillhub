from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass

@dataclass
class SkillInfo:
    """Information about a skill."""
    name: str
    scope: str
    source_path: Path
    platforms: list[str] | None = None  # None means all platforms

    @property
    def full_name(self) -> str:
        return f"@{self.scope}/{self.name}"

class SourceProvider(ABC):
    """Base class for source providers."""

    @abstractmethod
    def fetch(self, cache_dir: Path) -> list[SkillInfo]:
        """Fetch skills and return list of SkillInfo."""
        pass

    @abstractmethod
    def update(self, cache_dir: Path) -> list[SkillInfo]:
        """Update cached skills and return list of SkillInfo."""
        pass
