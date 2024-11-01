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

import os

from dotenv import load_dotenv


load_dotenv()


class Env:
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID")  # type: ignore
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET")  # type: ignore
    SPOTIFY_TRENDING_NOW_PLAYLIST_ID: str = os.getenv("SPOTIFY_TRENDING_NOW_PLAYLIST_ID")  # type: ignore
    SPOTIFY_TOP_100_PLAYLIST_ID: str = os.getenv("SPOTIFY_TOP_100_PLAYLIST_ID")  # type: ignore

    SRF_CLIENT_ID: str = os.getenv("SRF_CLIENT_ID")  # type: ignore
    SRF_CLIENT_SECRET: str = os.getenv("SRF_CLIENT_SECRET")  # type: ignore
    SENTRY_DSN: str = os.getenv("SENTRY_DSN")  # type: ignore
