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
                cache_handler=TokenCacheFileHandler("./.cache/.cache_spotify"),
            )
        )

    def _get_playlist_uris(self) -> List[str]:
        playlist_items = self.client.playlist_items(Env.SPOTIFY_PLAYLIST_ID)
        playlist_uris = []
        if playlist_items:
            playlist_uris = [item["track"]["uri"] for item in playlist_items["items"]]

        return playlist_uris

    def search_title(self, *, title: str, artist: str) -> Optional[str]:
        artist = re.sub("feat.", ",", artist, flags=re.IGNORECASE)
        q = f"{title} {artist}"
        search_results = self.client.search(q)

        track_uri = None
        if search_results:
            track = search_results["tracks"]["items"][0]
            track_uri = track["uri"]

        return track_uri

    def add_to_playlist(self, songs: List[Song]) -> None:
        playlist_uris = self._get_playlist_uris()
        items = []
        for song in songs:
            if song.uri not in playlist_uris:
                items.append(song.uri)

        if items:
            logger.info("add items to playlist")
            self.client.playlist_add_items(Env.SPOTIFY_PLAYLIST_ID, items=items)

    def remove_from_playlist(self, songs: List[Song]) -> None:
        playlist_uris = self._get_playlist_uris()
        items = []
        for song in songs:
            if song.uri in playlist_uris:
                items.append(song.uri)

        if items:
            logger.info("remove items from playlist")
            self.client.playlist_remove_all_occurrences_of_items(Env.SPOTIFY_PLAYLIST_ID, items=items)
