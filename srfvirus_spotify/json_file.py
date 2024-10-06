import json
import os
import logging
from typing import Any, Dict, Optional, TextIO


logger = logging.getLogger(__name__)


class JSONFile:

    def __init__(self, path: str):
        self.path: str = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                f.write("{}")

    def _clear(self, f: TextIO) -> None:
        f.seek(0)
        f.truncate(0)

    def get(self, key: str) -> Optional[Any]:
        with open(self.path, "r") as f:
            data = json.load(f)

        try:
            value = data[key]
        except KeyError:
            value = None
        return value

    def set(self, *, key: str, value: Any) -> None:
        with open(self.path, "r+") as f:
            data = json.load(f)
            data[key] = value

            self._clear(f)
            json.dump(data, f, indent=4)

    def delete(self, key: str) -> None:
        with open(self.path, "r+") as f:
            data = json.load(f)
            del data[key]

            self._clear(f)
            json.dump(data, f, indent=4)

    def read(self) -> Dict[str, Any]:
        with open(self.path, "r") as f:
            data = json.load(f)
        return data

    def write(self, data: Dict[str, Any]) -> None:
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
