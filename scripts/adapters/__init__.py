from .base import TargetAdapter
from .claude_adapter import ClaudeAdapter
from .codex_adapter import CodexAdapter
from .gemini_adapter import GeminiAdapter

def detect_platforms() -> list[TargetAdapter]:
    """Auto-detect installed platforms."""
    adapters = []
    for adapter_class in [ClaudeAdapter, CodexAdapter, GeminiAdapter]:
        adapter = adapter_class()
        if adapter.is_installed():
            adapters.append(adapter)
    return adapters

__all__ = [
    "TargetAdapter",
    "ClaudeAdapter",
    "CodexAdapter",
    "GeminiAdapter",
    "detect_platforms",
]
