from __future__ import annotations

from dataclasses import dataclass, field
from os import getenv

from ai_equity_discovery.memory.obsidian import ObsidianMemoryConfig


def _env_int(name: str, default: int) -> int:
    raw = getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class DiscoveryAgentConfig:
    enabled: bool = False
    provider: str = "openrouter"
    api_key: str = ""
    model: str = ""
    model_discovery: str = ""
    model_analysis: str = ""
    model_reporting: str = ""
    base_url: str = "https://openrouter.ai/api/v1"
    timeout_seconds: float = 25.0
    max_retries: int = 1
    batch_size: int = 10
    output_language: str = "en"


@dataclass(slots=True)
class AppConfig:
    x_accounts: list[str] = field(default_factory=list)
    reddit_subreddits: list[str] = field(default_factory=list)
    bootstrap_lookback_days: int = 7
    daily_lookback_days: int = 1
    discovery_agent: DiscoveryAgentConfig = field(default_factory=DiscoveryAgentConfig)
    memory: ObsidianMemoryConfig = field(default_factory=ObsidianMemoryConfig)

    @classmethod
    def from_env(cls, **overrides: object) -> "AppConfig":
        cfg = cls(
            bootstrap_lookback_days=_env_int("BOOTSTRAP_LOOKBACK_DAYS", 7),
            daily_lookback_days=_env_int("DAILY_LOOKBACK_DAYS", 1),
            discovery_agent=DiscoveryAgentConfig(
                enabled=_env_bool("DISCOVERY_AGENT_ENABLED", True),
                provider="openrouter",
                api_key=getenv("OPENROUTER_API_KEY", ""),
                model=getenv("OPENROUTER_MODEL", ""),
                model_discovery=getenv(
                    "OPENROUTER_MODEL_DISCOVERY", getenv("OPENROUTER_MODEL", "")
                ),
                model_analysis=getenv(
                    "OPENROUTER_MODEL_ANALYSIS",
                    getenv(
                        "OPENROUTER_MODEL_DISCOVERY", getenv("OPENROUTER_MODEL", "")
                    ),
                ),
                model_reporting=getenv(
                    "OPENROUTER_MODEL_REPORTING", getenv("OPENROUTER_MODEL", "")
                ),
                base_url=getenv(
                    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
                ).rstrip("/"),
                timeout_seconds=_env_float("OPENROUTER_TIMEOUT_SECONDS", 25.0),
                max_retries=_env_int("OPENROUTER_MAX_RETRIES", 1),
                batch_size=max(1, _env_int("DISCOVERY_AGENT_BATCH_SIZE", 10)),
                output_language=getenv("AGENT_OUTPUT_LANGUAGE", "en").strip() or "en",
            ),
            memory=ObsidianMemoryConfig(
                enabled=_env_bool("OBSIDIAN_MEMORY_ENABLED", True),
                vault_path=getenv("CLAUDE_VAULT", "").strip(),
                root_subdir=getenv(
                    "OBSIDIAN_MEMORY_ROOT",
                    "projects/ai-equity-discovery-agent/research",
                ).strip()
                or "projects/ai-equity-discovery-agent/research",
            ),
        )
        for key, value in overrides.items():
            setattr(cfg, key, value)
        return cfg
