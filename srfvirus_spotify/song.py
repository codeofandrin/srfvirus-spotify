import datetime
from typing import Dict, Any


class Song:

    def __init__(self, *, uri: str, data: Dict[str, Any]):
        self.uri: str = uri
        self.title: str = data["title"]
        self.artist: str = data["artist"]["name"]
        self._date: str = data["date"]

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
        dt = datetime.datetime.fromisoformat(self._date)
        return int(dt.timestamp())

    def to_dict(self) -> Dict[str, Any]:
        ret = {"title": self.title, "artist": self.artist, "timestamp": self.timestamp}
        return ret
