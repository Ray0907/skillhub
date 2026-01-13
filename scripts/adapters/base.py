from abc import ABC, abstractmethod
from pathlib import Path

class TargetAdapter(ABC):
    """Base class for platform adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Platform name (e.g., 'claude', 'codex', 'gemini')."""
        pass

    @property
    @abstractmethod
    def skills_dir(self) -> Path:
        """Path to skills directory."""
        pass

    def is_installed(self) -> bool:
        """Check if platform is installed."""
        return self.skills_dir.parent.exists()

    def install_skill(self, source_path: Path, skill_name: str) -> bool:
        """Install a skill to this platform."""
        target_path = self.skills_dir / skill_name
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if target_path.exists():
            import shutil
            shutil.rmtree(target_path)

        import shutil
        shutil.copytree(source_path, target_path)
        return True

    def list_installed(self) -> list[str]:
        """List installed skills."""
        if not self.skills_dir.exists():
            return []
        return [d.name for d in self.skills_dir.iterdir() if d.is_dir()]
