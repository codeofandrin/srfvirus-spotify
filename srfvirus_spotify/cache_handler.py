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
