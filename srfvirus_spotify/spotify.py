from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from spotipy import Spotify as SpotifyClient, SpotifyOAuth

from .env import Env
from .cache_handler import TokenCacheFileHandler

if TYPE_CHECKING:
    from .song import Song


logger = logging.getLogger(__name__)


SPOTIFY_PLAYLIST_ID = "6c6OWdem6i3ekL60K1SiKu"
SPOTIFY_SCOPES = "playlist-read-private,playlist-modify-private"


sp_client = SpotifyClient(
    auth_manager=SpotifyOAuth(
        client_id=Env.SPOTIFY_CLIENT_ID,
        client_secret=Env.SPOTIFY_CLIENT_SECRET,
        redirect_uri="http://example.com",
        scope=SPOTIFY_SCOPES,
        cache_handler=TokenCacheFileHandler("./.cache/.cache_spotify"),
    )
)


def search_title(*, title: str, artist: str) -> Optional[str]:
    q = f"{title} {artist}"
    search_results = sp_client.search(q)

    track_uri = None
    if search_results:
        track = search_results["tracks"]["items"][0]
        track_uri = track["uri"]

    return track_uri


def add_to_playlist(song: Song) -> None:
    playlist_items = sp_client.playlist_items(SPOTIFY_PLAYLIST_ID)
    if playlist_items:
        playlist_uris = [item["track"]["uri"] for item in playlist_items["items"]]
        if song.uri not in playlist_uris:
            sp_client.playlist_add_items(SPOTIFY_PLAYLIST_ID, items=[song.uri])


def remove_from_playlist(song: Song) -> None: ...
