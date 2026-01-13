#!/usr/bin/env python3
"""
SkillHub - Cross-platform Agent Skills Manager
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add scripts to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from adapters import detect_platforms, TargetAdapter
from providers import GitProvider, LocalProvider
from providers.base import SkillInfo

SKILLHUB_HOME = Path.home() / ".skillhub"
CONFIG_FILE = SKILLHUB_HOME / "config.json"
REMOTE_INDEX = SKILLHUB_HOME / "remote-index.json"
LOCAL_INDEX = SKILLHUB_HOME / "local-index.json"
STATE_FILE = SKILLHUB_HOME / "state.json"
CACHE_DIR = SKILLHUB_HOME / "cache"

# Ensure home directory exists
SKILLHUB_HOME.mkdir(parents=True, exist_ok=True)

def load_json(path: Path) -> dict:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        pass
    return {}

def save_json(path: Path, data: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
    except OSError:
        pass

def get_providers() -> list:
    """Build providers from index files."""
    providers = []

    remote_index = load_json(REMOTE_INDEX)
    for source in remote_index.get("sources", []):
        if source.get("type") == "git":
            providers.append(GitProvider(
                scope=source["scope"],
                url=source["url"],
                skills=source.get("skills")
            ))

    local_index = load_json(LOCAL_INDEX)
    for source in local_index.get("sources", []):
        if source.get("type") == "directory":
            providers.append(LocalProvider(
                scope=source["scope"],
                path=source["path"],
                skills=source.get("skills")
            ))

    return providers

def should_sync_to_platform(skill: SkillInfo, adapter: TargetAdapter) -> bool:
    """Check if skill should sync to given platform."""
    if skill.platforms is None:
        return True
    return adapter.name in skill.platforms

def cmd_sync(args: list) -> None:
    quiet = "--quiet" in args

    if not quiet:
        print("SkillHub Sync")
        print("=" * 40)

    # Detect platforms
    platforms = detect_platforms()
    if not quiet:
        print(f"Detected platforms: {[p.name for p in platforms]}")

    # Get all providers
    providers = get_providers()
    if not providers:
        if not quiet:
            print("No sources configured. Add sources to remote-index.json or local-index.json")
        return

    # Fetch skills from all providers
    all_skills: list[SkillInfo] = []
    for provider in providers:
        skills = provider.fetch(CACHE_DIR)
        all_skills.extend(skills)
        if not quiet:
            print(f"Found {len(skills)} skills from {provider.scope}")

    # Sync to platforms
    synced = []
    for skill in all_skills:
        for platform in platforms:
            if should_sync_to_platform(skill, platform):
                # Use namespaced directory: @scope/skill-name
                target_name = f"@{skill.scope}/{skill.name}"
                platform.install_skill(skill.source_path, target_name)
                synced.append((skill.full_name, platform.name))
                if not quiet:
                    print(f"  Synced {skill.full_name} -> {platform.name}")

    # Update state
    state = load_json(STATE_FILE)
    state["last_sync_time"] = datetime.now(timezone.utc).isoformat()
    state["installed_skills"] = list(set(s[0] for s in synced))
    save_json(STATE_FILE, state)

    if not quiet:
        print(f"\nSynced {len(synced)} skill-platform pairs")

def cmd_install(args: list) -> None:
    if not args:
        print("Usage: skillhub install @scope/name")
        return

    skill_ref = args[0]
    if not skill_ref.startswith("@"):
        print("Skill name must be in @scope/name format")
        return

    # Parse @scope/name
    parts = skill_ref[1:].split("/", 1)
    if len(parts) != 2:
        print("Invalid skill reference. Use @scope/name format")
        return

    scope, name = parts
    print(f"Installing {skill_ref}...")

    # Find in providers
    providers = get_providers()
    for provider in providers:
        if provider.scope == scope:
            skills = provider.fetch(CACHE_DIR)
            for skill in skills:
                if skill.name == name:
                    platforms = detect_platforms()
                    for platform in platforms:
                        if should_sync_to_platform(skill, platform):
                            target_name = f"@{skill.scope}/{skill.name}"
                            platform.install_skill(skill.source_path, target_name)
                            print(f"  Installed to {platform.name}")
                    return

    print(f"Skill {skill_ref} not found in configured sources")

def cmd_list(args: list) -> None:
    print("Available Skills")
    print("=" * 40)

    providers = get_providers()
    if not providers:
        print("No sources configured")
        return

    for provider in providers:
        skills = provider.fetch(CACHE_DIR)
        print(f"\n[@{provider.scope}]")
        for skill in skills:
            platforms_str = f" (platforms: {skill.platforms})" if skill.platforms else ""
            print(f"  {skill.full_name}{platforms_str}")

def cmd_status(args: list) -> None:
    state = load_json(STATE_FILE)
    config = load_json(CONFIG_FILE)

    print("SkillHub Status")
    print("=" * 40)
    print(f"Last sync: {state.get('last_sync_time', 'Never')}")
    print(f"Auto sync: {config.get('auto_sync', True)}")
    print(f"Sync interval: {config.get('sync_interval_hours', 24)}h")

    print("\nDetected Platforms:")
    for platform in detect_platforms():
        print(f"  - {platform.name}: {platform.skills_dir}")

    print(f"\nInstalled skills: {len(state.get('installed_skills', []))}")
    for skill in state.get("installed_skills", []):
        print(f"  - {skill}")

def cmd_config(args: list) -> None:
    config = load_json(CONFIG_FILE)

    if not args:
        print("SkillHub Configuration")
        print(json.dumps(config, indent=2))
        return

    # Simple key=value setting
    if "=" in args[0]:
        key, value = args[0].split("=", 1)
        # Try to parse as JSON for booleans/numbers
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
        config[key] = value
        save_json(CONFIG_FILE, config)
        print(f"Set {key} = {value}")

def cmd_check_auto_sync(args: list) -> None:
    """Check if auto-sync should run (called from hooks)."""
    config = load_json(CONFIG_FILE)
    state = load_json(STATE_FILE)

    if not config.get("auto_sync", True):
        return

    last_sync = state.get("last_sync_time")
    if last_sync is None:
        cmd_sync(["--quiet"])
        return

    last_sync_dt = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    hours_since = (now - last_sync_dt).total_seconds() / 3600

    interval = config.get("sync_interval_hours", 24)
    if hours_since >= interval:
        cmd_sync(["--quiet"])

def main() -> None:
    if len(sys.argv) < 2:
        print("SkillHub - Cross-platform Agent Skills Manager")
        print("\nUsage: skillhub <command> [args]")
        print("\nCommands:")
        print("  sync              Sync all skills to detected platforms")
        print("  install @s/n      Install specific skill")
        print("  list              List available skills")
        print("  status            Show sync status")
        print("  config [key=val]  View/set configuration")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "sync": cmd_sync,
        "install": cmd_install,
        "list": cmd_list,
        "status": cmd_status,
        "config": cmd_config,
        "check-auto-sync": cmd_check_auto_sync,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
