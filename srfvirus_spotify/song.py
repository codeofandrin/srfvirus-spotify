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

from typing import Dict, Any, Iterable, List, Set, TYPE_CHECKING, Optional

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
        duration_ms: Optional[int] = None,
        retained_at: Optional[int] = None,
        count: int = 0,
        in_playlist: bool = False,
    ):
        self.uri: str = uri
        self.title: str = title
        self.artist: str = artist
        self.played_at: int = played_at
        self.duration_ms: Optional[int] = duration_ms
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
            "duration_ms": self.duration_ms,
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
            duration_ms=data.get("duration_ms"),
            retained_at=data["retained_at"],
            count=data["count"],
            in_playlist=data["in_playlist"],
        )

    def retain(self) -> None:
        self.retained_at = self.played_at


class SongDuplicateChecker:
    """Flags a song as a duplicate of one already seen, either by Spotify URI
    or by matching title/artist with a near-identical duration (e.g. the same
    recording resolved to a different Spotify track id on a later search).
    """

    DURATION_TOLERANCE_MS = 2000

    def __init__(self, songs: Iterable[Song] = ()):
        self._seen_uris: Set[str] = set()
        self._seen_title_artist: Dict[str, List[int]] = {}
        for song in songs:
            self.add(song)

    def _key(self, song: Song) -> str:
        return f"{song.title}:{song.artist}".lower()

    def is_duplicate(self, song: Song) -> bool:
        if song.uri in self._seen_uris:
            return True

        if song.duration_ms is None:
            return False

        durations = self._seen_title_artist.get(self._key(song))
        if not durations:
            return False

        return any(abs(duration - song.duration_ms) < self.DURATION_TOLERANCE_MS for duration in durations)

    def add(self, song: Song) -> None:
        self._seen_uris.add(song.uri)
        if song.duration_ms is not None:
            self._seen_title_artist.setdefault(self._key(song), []).append(song.duration_ms)
