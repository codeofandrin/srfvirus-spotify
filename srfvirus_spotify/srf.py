"""
MIT License

Copyright (c) 2024 codeofandrin

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

import requests
import time
import datetime
import logging
import copy
from requests.auth import HTTPBasicAuth
from typing import List, Dict, Any, Optional
from zoneinfo import ZoneInfo

from .env import Env
from .cache_handler import TokenCacheFileHandler
from .errors import SRFHTTPException
from .storage_handler import SongsStorageFileHandler, SongsMetadataFileHandler
from .song import Song
from .spotify import SpotifyPlaylist, Spotify


logger = logging.getLogger(__name__)


SRF_BASE_URL = "https://api.srgssr.ch"
SRF_OAUTH_BASE_URL = f"{SRF_BASE_URL}/oauth/v1"
SRF_AUDIO_BASE_URL = f"{SRF_BASE_URL}/audiometadata/v2"
SRF_VIRUS_CHANNEL_ID = "66815fe2-9008-4853-80a5-f9caaffdf3a9"


class _SRFClient:

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        cache_handler: TokenCacheFileHandler,
    ):
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.cache_handler: TokenCacheFileHandler = cache_handler

        self.__token: str = self._get_token()

    def _request_token(self) -> Dict[str, Any]:
        response = requests.post(
            f"{SRF_OAUTH_BASE_URL}/accesstoken?grant_type=client_credentials",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
        )

        data = response.json()
        if 300 > response.status_code >= 200:
            return data
        else:
            raise SRFHTTPException(response=response, data=data)

    def _get_token(self) -> str:
        token_info = self.cache_handler.get_cached_token()
        if not token_info:
            token_info = self._request_token()
            self._save_token_info(token_info)

        return token_info["access_token"]

    def _save_token_info(self, token_info: Dict[str, Any]) -> None:
        # add expire time to token info
        now = int(time.time())
        expires_at = now + token_info["expires_in"]
        token_info["expires_at"] = expires_at

        self.cache_handler.save_token_to_cache(token_info)

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # check if new token must be requested
        token_info = self.cache_handler.get_cached_token()
        expires_at = token_info["expires_at"]
        now = int(time.time())

        # use an offset of 1 minute as a buffer
        if now >= (expires_at - 60):
            token_info = self._request_token()
            self._save_token_info(token_info)
            self.__token = self._get_token()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__token}",
        }

        response = requests.request(
            method=method,
            url=f"{SRF_AUDIO_BASE_URL}{url}",
            headers=headers,
            params=params,
            json=payload,
        )

        data = response.json()

        if 300 > response.status_code >= 200:
            return data
        else:
            raise SRFHTTPException(response=response, data=data)

    def fetch_radio_channels(self) -> List[Dict[str, Any]]:
        params = {"bu": "srf"}
        data = self._request("GET", "/radio/channels", params=params)
        return data["channelList"]

    def fetch_song_list(self, channel_id: str) -> List[Dict[str, Any]]:
        params = {"bu": "srf", "channelId": channel_id}
        data = self._request("GET", "/radio/songlist", params=params)
        return data["songList"]


class SRF:

    def __init__(self):
        self.client: _SRFClient = _SRFClient(
            client_id=Env.SRF_CLIENT_ID,
            client_secret=Env.SRF_CLIENT_SECRET,
            cache_handler=TokenCacheFileHandler("./.cache/.srf_token"),
        )
        self.spotify: Spotify = Spotify()
        self.metadata: SongsMetadataFileHandler = SongsMetadataFileHandler(f"./storage/songs_metadata.json")
        self.current_songs: List[Song] = self._get_current_songs()

    def _get_current_songs(self) -> List[Song]:
        data = self.client.fetch_song_list(SRF_VIRUS_CHANNEL_ID)
        last_timestamp = self.metadata.get("last_timestamp")

        songs = []
        for raw_song in data:
            # check timestamp first to not search songs that are
            # redundant from last request (and therefore not needed)
            dt = datetime.datetime.fromisoformat(raw_song["date"])
            played_at = int(dt.timestamp())
            if played_at == last_timestamp:
                break

            uri = self.spotify.search_title(title=raw_song["title"], artist=raw_song["artist"]["name"])
            if uri is not None:
                song = Song(
                    uri=uri,
                    title=raw_song["title"],
                    artist=raw_song["artist"]["name"],
                    played_at=played_at,
                )
                songs.append(song)

            time.sleep(1)

        if songs:
            self.metadata.set("last_timestamp", songs[0].played_at)

        return songs


class SongCollection:

    def __init__(self, *, srf: SRF, playlist_id: str, name: str):
        self._srf: SRF = srf
        self.playlist = SpotifyPlaylist(client=self._srf.spotify.client, id=playlist_id, name=name)
        self.songs: SongsStorageFileHandler = SongsStorageFileHandler(f"./storage/songs_{name}.json")
        self.current_songs: List[Song] = copy.deepcopy(self._srf.current_songs)

    def _get_current_songs(self) -> List[Song]:
        songs = []
        for current_song in self.current_songs:
            # check if song is already stored
            stored_song = self.songs.get(current_song.uri)
            if stored_song is not None:
                stored_song.played_at = current_song.played_at
                songs.append(stored_song)
            else:
                songs.append(current_song)

        return songs

    def get_new_songs(self) -> List[Song]:
        raise NotImplementedError

    def get_old_songs(self) -> List[Song]:
        raise NotImplementedError


class TrendingNowCollection(SongCollection):

    REQUIRED_SONG_COUNT = 3
    SONG_DEADLINE = int(datetime.timedelta(weeks=1).total_seconds())

    def __init__(self, *, srf: SRF):
        super().__init__(
            srf=srf,
            playlist_id=Env.SPOTIFY_TRENDING_NOW_PLAYLIST_ID,
            name="trending_now",
        )

    def _is_past_deadline(self, song: Song) -> bool:
        now = int(time.time())
        return now >= (song.retained_at + self.SONG_DEADLINE)

    def get_new_songs(self) -> List[Song]:
        logger.info("get new songs for 'trending now'")

        new_songs = []
        for song in self._get_current_songs():
            # check retention to potentially prevent adding song
            # that is not played enough
            if self._is_past_deadline(song):
                song.count = 0

            song.count += 1
            # if song reaches specific count, it's a trending song
            if song.count >= self.REQUIRED_SONG_COUNT:
                song.count = 0
                # retain to prevent song being removed later
                song.retain()
                if not song.in_playlist:
                    song.in_playlist = True
                    new_songs.append(song)

            # always update it in storage to update at least played_at timestamp
            self.songs.set(song)

        return new_songs

    def get_old_songs(self) -> List[Song]:
        logger.info("get old songs for 'trending now'")
        songs = self.songs.get_all()
        old_songs = []
        for song in songs:
            # if it's past deadline, it wasn't played enough to be retained
            if song.in_playlist and self._is_past_deadline(song):
                self.songs.remove(song)
                old_songs.append(song)

        return old_songs


class Top100Collection(SongCollection):

    SONG_DEADLINE = int(datetime.timedelta(weeks=2).total_seconds())

    def __init__(self, *, srf: SRF):
        super().__init__(
            srf=srf,
            playlist_id=Env.SPOTIFY_TOP_100_PLAYLIST_ID,
            name="top_100",
        )

    def _get_sorted_all_songs(self) -> List[Song]:
        songs = self.songs.get_all()
        # sort by ...
        # 1. count, high to low
        # 2. played_at, low to high
        songs = sorted(songs, key=lambda x: x.played_at)
        songs = sorted(songs, key=lambda x: x.count, reverse=True)

        return songs

    def _is_past_deadline(self, song: Song) -> bool:
        now = int(time.time())
        return now >= (song.retained_at + self.SONG_DEADLINE)

    def get_new_songs(self) -> List[Song]:
        logger.info("get new songs for 'top 100'")

        for song in self._get_current_songs():
            # check retention to potentially prevent adding song
            # that is not played enough
            if self._is_past_deadline(song):
                song.count = 0

            song.count += 1
            # retain to prevent song being removed later
            song.retain()
            self.songs.set(song)

        sorted_all_songs = self._get_sorted_all_songs()
        new_songs = []
        for song in sorted_all_songs[:100]:
            if not song.in_playlist:
                song.in_playlist = True
                self.songs.set(song)
                new_songs.append(song)

        return new_songs

    def get_old_songs(self) -> List[Song]:
        logger.info("get old songs for 'top 100'")

        old_songs = []
        # remove songs which are not played anymore
        all_songs = self.songs.get_all()
        for song in all_songs:
            if song.in_playlist and self._is_past_deadline(song):
                self.songs.remove(song)
                old_songs.append(song)

        # remove songs beyond top 100
        sorted_all_songs = self._get_sorted_all_songs()
        for song in sorted_all_songs[100:]:
            if song.in_playlist:
                song.in_playlist = False
                self.songs.set(song)
                old_songs.append(song)

        return old_songs


class NightOutCollection(SongCollection):

    SONG_DEADLINE = int(datetime.timedelta(weeks=3).total_seconds())

    def __init__(self, srf: SRF):
        super().__init__(
            srf=srf,
            playlist_id=Env.SPOTIFY_NIGHT_OUT_PLAYLIST_ID,
            name="night_out",
        )

    def _is_past_deadline(self, song: Song) -> bool:
        now = int(time.time())
        return now >= (song.retained_at + self.SONG_DEADLINE)

    def _is_night_out_song(self, song: Song) -> bool:
        tz = ZoneInfo("Europe/Zurich")
        played_at = datetime.datetime.fromtimestamp(song.played_at).astimezone(tz)
        return played_at.isoweekday() == 6 and played_at.hour >= 20

    def get_new_songs(self) -> List[Song]:
        logger.info("get new songs for 'night out'")

        new_songs = []
        for song in self._get_current_songs():
            if self._is_night_out_song(song):
                # retain to prevent song being removed later
                song.retain()
                if not song.in_playlist:
                    song.in_playlist = True
                    new_songs.append(song)

                # always update it in storage to update at least played_at timestamp
                self.songs.set(song)

        return new_songs

    def get_old_songs(self) -> List[Song]:
        logger.info("get old songs for 'night out'")

        songs = self.songs.get_all()
        old_songs = []
        for song in songs:
            # if it's past deadline, it wasn't played enough to be retained
            if song.in_playlist and self._is_past_deadline(song):
                self.songs.remove(song)
                old_songs.append(song)

        return old_songs
