from __future__ import annotations

import json
from pathlib import Path


MEMORY_FILE = Path("data/user_memory.json")


class MemoryService:

    def __init__(self) -> None:
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not MEMORY_FILE.exists():
            MEMORY_FILE.write_text(
                "{}",
                encoding="utf-8",
            )

    def get_memory(self, user_id: int) -> dict:
        try:
            data = json.loads(
                MEMORY_FILE.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            return {}

        return data.get(str(user_id), {})

    def save_memory(
        self,
        user_id: int,
        key: str,
        value: str,
    ) -> None:

        try:
            data = json.loads(
                MEMORY_FILE.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            data = {}

        data.setdefault(str(user_id), {})
        data[str(user_id)][key] = value

        MEMORY_FILE.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
