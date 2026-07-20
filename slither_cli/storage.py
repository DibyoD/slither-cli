"""Local persistence for high scores. No network, no accounts — just a JSON file."""

from __future__ import annotations

import json
import os
from pathlib import Path


def _data_dir() -> Path:
    """Return the per-user data directory, honoring XDG_DATA_HOME on Linux/macOS."""
    base = os.environ.get("XDG_DATA_HOME")
    if base:
        root = Path(base)
    else:
        root = Path.home() / ".local" / "share"
    directory = root / "slither-cli"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _score_file() -> Path:
    return _data_dir() / "highscore.json"


def load_stats() -> dict:
    """Load persisted stats. Always returns a well-formed dict."""
    defaults = {"high_score": 0, "games_played": 0}
    try:
        with _score_file().open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return defaults
        return {
            "high_score": int(data.get("high_score", 0)),
            "games_played": int(data.get("games_played", 0)),
        }
    except (OSError, ValueError, TypeError):
        return defaults


def save_stats(stats: dict) -> None:
    """Persist stats, swallowing any I/O errors so the game never crashes on save."""
    try:
        tmp = _score_file().with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(stats, fh)
        tmp.replace(_score_file())
    except OSError:
        pass


def record_game(score: int) -> tuple[int, bool]:
    """Record a finished game. Returns (high_score, is_new_record)."""
    stats = load_stats()
    stats["games_played"] += 1
    is_record = score > stats["high_score"]
    if is_record:
        stats["high_score"] = score
    save_stats(stats)
    return stats["high_score"], is_record
