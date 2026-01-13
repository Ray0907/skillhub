from pathlib import Path
from .base import SourceProvider, SkillInfo

class LocalProvider(SourceProvider):
    def __init__(self, scope: str, path: str, skills: list[str] | None = None):
        self.scope = scope
        self.path = Path(path).expanduser()
        self.skills_filter = skills

    def _find_skills(self) -> list[SkillInfo]:
        """Find SKILL.md files in local directory."""
        skills = []

        try:
            if not self.path.exists():
                return skills

            for skill_md in self.path.rglob("SKILL.md"):
                skill_dir = skill_md.parent
                skill_name = skill_dir.name

                # Filter if specified
                if self.skills_filter and "*" not in self.skills_filter:
                    if skill_name not in self.skills_filter:
                        continue

                skills.append(SkillInfo(
                    name=skill_name,
                    scope=self.scope,
                    source_path=skill_dir,
                    platforms=None
                ))
        except (OSError, IOError):
            # File system error - return whatever skills found so far
            pass

        return skills

    def fetch(self, cache_dir: Path) -> list[SkillInfo]:
        return self._find_skills()

    def update(self, cache_dir: Path) -> list[SkillInfo]:
        return self._find_skills()
