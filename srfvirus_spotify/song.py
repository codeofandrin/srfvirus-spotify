from __future__ import annotations

import datetime
from typing import Dict, Any, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing_extensions import Self


class Song:

    def __init__(
        self,
        *,
        uri: str,
        data: Dict[str, Any],
        played_at: Optional[int] = None,
        retained_at: Optional[int] = None,
        count: int = 0,
        in_playlist: bool = False,
    ):
        self.uri: str = uri
        self.title: str = data["title"]
        self.artist: str = data["artist"]["name"]
        self._date: str = data["date"]
        self._played_at: Optional[int] = played_at
        self.count: int = count
        self.in_playlist: bool = in_playlist
        self.retained_at: int
        if retained_at is not None:
            self.retained_at = retained_at
        else:
            self.retain()

    def __repr__(self) -> str:
        attrs = (
            ("uri", self.uri),
            ("title", self.title),
            ("artist", self.artist),
            ("played_at", self.played_at),
        )
        joined = " ".join([f"{k}={v!r}" for k, v in attrs])
        return f"<Song {joined}>"

    @property
    def played_at(self) -> int:
        if self._played_at is None:
            dt = datetime.datetime.fromisoformat(self._date)
            played_at = int(dt.timestamp())
        else:
            played_at = self._played_at

        return played_at

    def to_storage_dict(self) -> Dict[str, Any]:
        ret = {
            "title": self.title,
            "artist": self.artist,
            "played_at": self.played_at,
            "retained_at": self.retained_at,
            "count": self.count,
            "in_playlist": self.in_playlist,
        }
        return ret

    @classmethod
    def from_storage_dict(cls, *, data: Dict[str, Any], uri: str) -> Self:
        new_data = {"title": data["title"], "artist": {"name": data["artist"]}, "date": ""}
        return cls(
            uri=uri,
            data=new_data,
            played_at=data["played_at"],
            retained_at=data["retained_at"],
            count=data["count"],
            in_playlist=data["in_playlist"],
        )

    def retain(self) -> None:
        self.retained_at = self.played_at
