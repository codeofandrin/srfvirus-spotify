from __future__ import annotations

import datetime
from typing import Dict, Any, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import Self


class Song:

    def __init__(self, *, uri: str, data: Dict[str, Any], timestamp: Optional[int] = None):
        self.uri: str = uri
        self.title: str = data["title"]
        self.artist: str = data["artist"]["name"]
        self._date: str = data["date"]
        self._timestamp: Optional[int] = timestamp

    def __repr__(self) -> str:
        attrs = (
            ("uri", self.uri),
            ("title", self.title),
            ("artist", self.artist),
            ("timestamp", self.timestamp),
        )
        joined = " ".join([f"{k}={v!r}" for k, v in attrs])
        return f"<Song {joined}>"

    @property
    def timestamp(self) -> int:
        if self._timestamp is None:
            dt = datetime.datetime.fromisoformat(self._date)
            timestamp = int(dt.timestamp())
        else:
            timestamp = self._timestamp

        return timestamp

    def to_storage_dict(self) -> Dict[str, Any]:
        ret = {"title": self.title, "artist": self.artist, "timestamp": self.timestamp}
        return ret

    @classmethod
    def from_storage_dict(cls, *, data: Dict[str, Any], uri: str) -> Self:
        new_data = {"title": data["title"], "artist": {"name": data["artist"]}, "date": ""}
        return Song(uri=uri, data=new_data, timestamp=data["timestamp"])
