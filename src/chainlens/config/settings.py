"""Configuration loader — env vars + YAML config files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "src" / "chainlens" / "config"


class ChainConfig(BaseModel):
    """Configuration for a single blockchain network."""

    rpc_url: str = ""
    explorer_api_url: str = ""
    explorer_api_key: str = ""
    chain_id: int = 1
    native_currency: str = "ETH"
    block_time_seconds: float = 12.0


class ScoringWeights(BaseModel):
    """Risk-scoring weights per signal (loaded from config, never hard-coded)."""

    owner_admin_privileges: float = 25.0
    mint_authority: float = 20.0
    honeypot: float = 30.0  # hard-cap signal
    liquidity_not_locked: float = 20.0
    holder_concentration_hhi: float = 15.0
    unverified_source: float = 10.0
    contract_age_low: float = 5.0
    critical_signals: list[str] = Field(default_factory=lambda: ["honeypot"])


class QuantParams(BaseModel):
    """Quantitative engine parameters: min samples, annualization, outlier threshold."""

    n_min_samples: int = 30
    annualization_periods: int = 365
    outlier_zscore_threshold: float = 3.0
    max_gap_fraction: float = 0.05


class AppConfig(BaseModel):
    """Top-level application configuration — merges YAML defaults with env overrides."""

    env: str = "development"

    # Cost control
    cost_ceiling_usd: float = 5.0
    max_calls_per_run: int = 1000

    # Cache
    cache_dir: str = ".cache"
    cache_ttl_hours: int = 6

    # Logging
    log_level: str = "INFO"
    log_format: str = "structured"

    # Scoring
    scoring: ScoringWeights = Field(default_factory=ScoringWeights)

    # Quant
    quant: QuantParams = Field(default_factory=QuantParams)

    # Chains
    chains: dict[str, ChainConfig] = Field(default_factory=dict)

    # Market data provider
    market_data_provider: str = "coingecko"
    market_data_api_key: str = ""

    # Default chain
    default_chain: str = "ethereum"

    @property
    def n_min(self) -> int:
        """Shorthand for quant.n_min_samples."""
        return self.quant.n_min_samples


def load_env() -> None:
    """Load .env file from project root."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def load_yaml_config(name: str) -> dict[str, Any]:
    """Load a YAML config file from config directory."""
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_config() -> AppConfig:
    """Build AppConfig from env vars + YAML defaults."""
    load_env()

    # Load base config from YAML
    base = load_yaml_config("defaults.yaml")

    # List of keys that can be overridden by env vars.
    # Remove them from base first so we don't pass them twice.
    env_overrides: dict[str, Any] = {
        "cost_ceiling_usd": float(
            os.getenv("COST_CEILING_USD", base.get("cost_ceiling_usd", 5.0))
        ),
        "max_calls_per_run": int(
            os.getenv("MAX_CALLS_PER_RUN", base.get("max_calls_per_run", 1000))
        ),
        "cache_dir": os.getenv("CACHE_DIR", base.get("cache_dir", ".cache")),
        "cache_ttl_hours": int(
            os.getenv("CACHE_TTL_HOURS", base.get("cache_ttl_hours", 6))
        ),
        "log_level": os.getenv("LOG_LEVEL", base.get("log_level", "INFO")),
        "log_format": os.getenv("LOG_FORMAT", base.get("log_format", "structured")),
        "market_data_api_key": os.getenv("MARKET_DATA_API_KEY", ""),
        "market_data_provider": os.getenv(
            "MARKET_DATA_PROVIDER", base.get("market_data_provider", "coingecko")
        ),
    }

    for k in env_overrides:
        base.pop(k, None)

    return AppConfig(**base, **env_overrides)
