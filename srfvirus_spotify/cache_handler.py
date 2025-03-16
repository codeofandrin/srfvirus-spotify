"""
MIT License

Copyright (c) 2025 codeofandrin

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

import logging
from typing import Dict, Any

from spotipy import CacheHandler

from .json_file import JSONFile


logger = logging.getLogger(__name__)


class TokenCacheFileHandler(CacheHandler):
    def __init__(self, cache_path: str):
        self.json_file: JSONFile = JSONFile(cache_path)

    def get_cached_token(self) -> Dict[str, Any]:
        token_info = self.json_file.read()
        if token_info is None:
            raise ValueError("token_info could not be retrieved")

        return token_info

    def save_token_to_cache(self, token_info: Dict[str, Any]) -> None:
        self.json_file.write(token_info)
