"""
MIT License

Copyright (c) 2024 Puncher1

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


class Spotify:

    SCOPES = "playlist-read-private,playlist-modify-private,playlist-modify-public"

    def __init__(self):
        self.client = SpotifyClient(
            auth_manager=SpotifyOAuth(
                client_id=Env.SPOTIFY_CLIENT_ID,
                client_secret=Env.SPOTIFY_CLIENT_SECRET,
                redirect_uri="http://example.com",
                scope=self.SCOPES,
                cache_handler=TokenCacheFileHandler("./.cache/.spotify_token"),
            )
        )

    def search_title(self, *, title: str, artist: str) -> Optional[str]:
        artist = re.sub("feat.", ",", artist, flags=re.IGNORECASE)
        q = f"{title} {artist}"
        search_results = self.client.search(q)

        track_uri = None
        if search_results:
            track = search_results["tracks"]["items"][0]
            track_uri = track["uri"]

        return track_uri


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
