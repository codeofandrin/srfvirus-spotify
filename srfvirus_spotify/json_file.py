"""
MIT License

Copyright (c) 2024 codeofandrin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import logging
from typing import Any, Dict, Optional, TextIO


logger = logging.getLogger(__name__)


class JSONFile:

    def __init__(self, path: str):
        self.path: str = path
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
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
