import json
from pathlib import Path
from typing import Any, Dict

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json_file(filename: str, default: Any = None) -> Any:
    """
    Load a JSON file from the shared data directory. If the file does not exist,
    optionally seed it with `default`.
    """
    ensure_data_dir()
    path = DATA_DIR / filename
    if not path.exists():
        if default is not None:
            path.write_text(json.dumps(default, indent=2), encoding="utf-8")
            return default
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(filename: str, payload: Any) -> None:
    """Persist payload into the shared data directory."""
    ensure_data_dir()
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
