import logging
from typing import Any, Optional, List

from .json_file import JSONFile
from .song import Song


logger = logging.getLogger(__name__)


SONG_ENCODE_FORMAT: str = "{title}:{artist}"


class SongsStorageFileHandler:

    def __init__(self, storage_path: str):
        self._json_file: JSONFile = JSONFile(storage_path)

    def set(self, song: Song) -> None:
        song_info = song.to_dict()
        self._json_file.set(key=song.uri, value=song_info)

    def remove(self, song: Song) -> None:
        self._json_file.delete(song.uri)

    def get_all(self) -> List[Song]:
        data = self._json_file.read()
        songs = []
        for uri, song_info in data.items():
            songs.append(Song(data=song_info, uri=uri))
        return songs


class SongsMetadataFileHandler:

    def __init__(self, storage_path: str):
        self.json_file: JSONFile = JSONFile(storage_path)

    def get(self, key: str) -> Optional[Any]:
        metadata = self.json_file.get(key)
        return metadata

    def set(self, key: str, value: Any) -> None:
        self.json_file.set(key=key, value=value)