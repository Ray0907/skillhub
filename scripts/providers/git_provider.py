import re
import subprocess
from pathlib import Path
from .base import SourceProvider, SkillInfo

class GitProvider(SourceProvider):
    def __init__(self, scope: str, url: str, skills: list[str] | None = None):
        self.scope = scope
        self.url = url
        self.skills_filter = skills  # None or ["*"] means all

    def _clone_or_pull(self, cache_dir: Path) -> Path | None:
        """Clone repo or pull if exists. Returns None on failure."""
        repo_dir = cache_dir / f"@{self.scope}"
        repo_dir.mkdir(parents=True, exist_ok=True)

        repo_name = self.url.rstrip("/").split("/")[-1].replace(".git", "")
        local_path = repo_dir / repo_name

        try:
            if local_path.exists():
                result = subprocess.run(
                    ["git", "-C", str(local_path), "pull", "--ff-only"],
                    capture_output=True,
                    check=True
                )
            else:
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", self.url, str(local_path)],
                    capture_output=True,
                    check=True
                )
            return local_path
        except subprocess.CalledProcessError as e:
            # Git command failed - return existing path if available, else None
            if local_path.exists():
                return local_path
            return None
        except OSError as e:
            # Git binary not found or other OS error
            return None

    def _find_skills(self, repo_path: Path) -> list[SkillInfo]:
        """Find SKILL.md files in repo."""
        skills = []
        for skill_md in repo_path.rglob("SKILL.md"):
            skill_dir = skill_md.parent
            skill_name = skill_dir.name

            # Filter if specified
            if self.skills_filter and "*" not in self.skills_filter:
                if skill_name not in self.skills_filter:
                    continue

            # Parse platforms from frontmatter if present
            platforms = self._parse_platforms(skill_md)

            skills.append(SkillInfo(
                name=skill_name,
                scope=self.scope,
                source_path=skill_dir,
                platforms=platforms
            ))

        return skills

    def _parse_platforms(self, skill_md: Path) -> list[str] | None:
        """Parse platforms field from SKILL.md frontmatter."""
        try:
            content = skill_md.read_text()
            match = re.search(r"^platforms:\s*\[(.*?)\]", content, re.MULTILINE)
            if match:
                platforms_str = match.group(1)
                return [p.strip().strip("'\"") for p in platforms_str.split(",")]
        except (OSError, IOError):
            # File read error - return None for platforms
            pass
        return None

    def fetch(self, cache_dir: Path) -> list[SkillInfo]:
        repo_path = self._clone_or_pull(cache_dir)
        if repo_path is None:
            return []
        return self._find_skills(repo_path)

    def update(self, cache_dir: Path) -> list[SkillInfo]:
        return self.fetch(cache_dir)
