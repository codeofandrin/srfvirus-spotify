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

import logging
import re
from typing import TYPE_CHECKING, Optional, List

from spotipy import Spotify as SpotifyClient, SpotifyOAuth

from .env import Env
from .cache_handler import TokenCacheFileHandler

if TYPE_CHECKING:
    from .song import Song


logger = logging.getLogger(__name__)

_COUNTRY_TAG_RE = re.compile(r"\s*\([A-Za-z]{2}\)")
_FEAT_RE = re.compile(r"\s+(?:feat\.?|ft\.?|featuring)\s+.*$", flags=re.IGNORECASE)
_PRIMARY_SPLIT_RE = re.compile(r"\s*[/,]\s*")


def _clean_artist(artist: str) -> str:
    return _COUNTRY_TAG_RE.sub("", artist).strip()


def _primary_artist(artist: str) -> str:
    artist = _FEAT_RE.sub("", _clean_artist(artist))
    return _PRIMARY_SPLIT_RE.split(artist)[0].strip()


class Spotify:

    SCOPES = "playlist-read-private,playlist-modify-private,playlist-modify-public"

    def __init__(self):
        self.client = SpotifyClient(
            auth_manager=SpotifyOAuth(
                client_id=Env.SPOTIFY_CLIENT_ID,
                client_secret=Env.SPOTIFY_CLIENT_SECRET,
                redirect_uri="https://example.com",
                scope=self.SCOPES,
                cache_handler=TokenCacheFileHandler("./.cache/.spotify_token"),
            ),
            requests_timeout=10,
        )

    def search_title(self, *, title: str, artist: str) -> Optional[str]:
        title = title.replace('"', " ").strip()
        primary_artist = _primary_artist(artist).replace('"', " ").strip()

        # Search in 3 stages:
        #   1. Precise matching with filters ("track:<track> artist:<primary artist>")
        #   2. Free text fallbacks ("<track> <primary artist>")
        #   3. Full text search (only "(CH)" stripped)
        queries = [
            f'track:"{title}" artist:"{primary_artist}"',
            f"{title} {primary_artist}",
            f"{title} {_clean_artist(artist)}",
        ]

        for q in queries:
            items = self._search_items(q)
            if items:
                return items[0]["uri"]

        logger.info(f"no spotify match for {title!r} by {artist!r}")
        return None

    def _search_items(self, q: str) -> List[dict]:
        search_results = self.client.search(q, limit=1)
        return ((search_results or {}).get("tracks") or {}).get("items") or []


class SpotifyPlaylist:

    def __init__(self, *, client: SpotifyClient, id: str, name: str):
        self._client: SpotifyClient = client
        self.id: str = id
        self.name: str = name

    def __repr__(self) -> str:
        return f"<SpotifyPlaylist id={self.id} name={self.name}>"

    def add_songs(self, songs: List[Song]) -> None:
        items = []
        for song in songs:
            items.append(song.uri)

        if items:
            logger.info(f"add items to playlist '{self.name.replace('_', ' ')}'")
            self._client.playlist_add_items(self.id, items=items)

    def remove_songs(self, songs: List[Song]) -> None:
        items = []
        for song in songs:
            items.append(song.uri)

        if items:
            logger.info(f"remove items from playlist '{self.name.replace('_', ' ')}'")
            self._client.playlist_remove_all_occurrences_of_items(self.id, items=items)
