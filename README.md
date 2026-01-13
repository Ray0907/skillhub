# SkillHub

Cross-platform Agent Skills manager for Claude Code, Codex CLI, and Gemini CLI.

SkillHub syncs skills from git repositories and local directories to all installed AI coding platforms.

## Features

- **Cross-platform sync**: Automatically detect and sync to Claude Code, Codex CLI, and Gemini CLI
- **Multiple sources**: Pull skills from git repos and local directories
- **Namespace isolation**: Skills use `@scope/name` format to avoid conflicts
- **Auto-sync**: Optional background sync on configurable intervals
- **Platform filtering**: Skills can specify which platforms they support

## Example Skill

Want to create your own skill? Check out this example:

- [arxiv-research-skill](https://github.com/Ray0907/arxiv-research-skill) - A skill for researching papers on arXiv

Skills use a simple structure:

```
my-skill/
├── SKILL.md          # Required: name, description, instructions
├── scripts/          # Optional: executable scripts
└── references/       # Optional: additional docs
```

## Installation

### Quick Install

```bash
# Clone this repo
git clone https://github.com/Ray0907/skillhub.git

# Copy to your Claude Code skills directory
cp -r skillhub ~/.claude/skills/

# Initialize SkillHub config
mkdir -p ~/.skillhub
python3 ~/.claude/skills/skillhub/scripts/skillhub.py status
```

### Deploy to Other Platforms

```bash
# Codex CLI
cp -r ~/.claude/skills/skillhub ~/.codex/skills/

# Gemini CLI
cp -r ~/.claude/skills/skillhub ~/.gemini/skills/
```

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `/skillhub sync` | Sync all skills to all detected platforms |
| `/skillhub install @scope/name` | Install a specific skill |
| `/skillhub list` | List available skills from all sources |
| `/skillhub status` | Show sync status and detected platforms |
| `/skillhub config` | View configuration |
| `/skillhub config key=value` | Set configuration value |

### Examples

```bash
# Check status
/skillhub status

# Sync all skills
/skillhub sync

# Install specific skill
/skillhub install @anthropic/tdd

# List available skills
/skillhub list

# Enable/disable auto-sync
/skillhub config auto_sync=true
/skillhub config sync_interval_hours=12
```

## Configuration

SkillHub stores configuration in `~/.skillhub/`:

```
~/.skillhub/
├── config.json           # User settings
├── remote-index.json     # Git repository sources
├── local-index.json      # Local directory sources
├── state.json            # Sync state
└── cache/                # Cloned repositories
```

### config.json

```json
{
  "sync_interval_hours": 24,
  "auto_sync": true,
  "default_targets": "auto"
}
```

### remote-index.json

Add git repositories as skill sources:

```json
{
  "version": 1,
  "sources": [
    {
      "scope": "anthropic",
      "type": "git",
      "url": "https://github.com/anthropics/skills",
      "skills": ["*"]
    },
    {
      "scope": "myorg",
      "type": "git",
      "url": "https://github.com/myorg/skills",
      "skills": ["tdd", "debugging"]
    }
  ]
}
```

### local-index.json

Add local directories as skill sources:

```json
{
  "version": 1,
  "sources": [
    {
      "scope": "local",
      "type": "directory",
      "path": "~/my-skills",
      "skills": ["*"]
    }
  ]
}
```

## Skill Namespace

Skills are installed with namespace prefixes to avoid conflicts:

```
~/.claude/skills/
├── @anthropic/
│   ├── tdd/
│   └── debugging/
├── @local/
│   └── my-custom-skill/
└── skillhub/
```

## Platform Detection

SkillHub automatically detects installed platforms by checking:

- Claude Code: `~/.claude/`
- Codex CLI: `~/.codex/`
- Gemini CLI: `~/.gemini/`

Skills are synced to all detected platforms.

## Platform-Specific Skills

Skills can specify which platforms they support in their `SKILL.md` frontmatter:

```yaml
---
name: claude-only-skill
description: A skill that only works with Claude Code
platforms: [claude]
---
```

## Directory Structure

```
skillhub/
├── SKILL.md              # Skill definition
├── README.md             # This file
└── scripts/
    ├── skillhub.py       # Main CLI
    ├── adapters/         # Platform adapters
    │   ├── __init__.py
    │   ├── base.py
    │   ├── claude_adapter.py
    │   ├── codex_adapter.py
    │   └── gemini_adapter.py
    └── providers/        # Source providers
        ├── __init__.py
        ├── base.py
        ├── git_provider.py
        └── local_provider.py
```

## Requirements

- Python 3.9+
- Git (for cloning remote repositories)

## License

MIT
