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

from __future__ import annotations

from typing import Dict, Any, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing_extensions import Self


class Song:

    def __init__(
        self,
        *,
        uri: str,
        title: str,
        artist: str,
        played_at: int,
        retained_at: Optional[int] = None,
        count: int = 0,
        in_playlist: bool = False,
    ):
        self.uri: str = uri
        self.title: str = title
        self.artist: str = artist
        self.played_at: int = played_at
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
        return cls(
            uri=uri,
            title=data["title"],
            artist=data["artist"],
            played_at=data["played_at"],
            retained_at=data["retained_at"],
            count=data["count"],
            in_playlist=data["in_playlist"],
        )

    def retain(self) -> None:
        self.retained_at = self.played_at
