from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def ensure_parent(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def write_json(path: str | Path, data: Any) -> Path:
    p = ensure_parent(path)
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif isinstance(data, list):
        data = [x.model_dump() if hasattr(x, "model_dump") else x for x in data]
    p.write_text(json.dumps(data, indent=2, default=str))
    return p

def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text())
