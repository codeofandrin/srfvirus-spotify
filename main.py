"""
MIT License

Copyright (c) 2026 codeofandrin

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

import logging
import datetime
import time

import sentry_sdk as sentry
from apscheduler.schedulers.blocking import BlockingScheduler

from srfvirus_spotify.srf import SRF, TrendingNowCollection, Top100Collection, NightOutCollection
from srfvirus_spotify.env import Env
from srfvirus_spotify.log import setup_logging
from srfvirus_spotify import reauth_services
from srfvirus_spotify.reauth import ensure_token_valid, remind_if_expiry_near, reauth_window_active
from srfvirus_spotify.errors import ReauthRequired


logger = logging.getLogger(__name__)


def sync_reauth_services() -> None:
    """Tunnel + callback server run exactly while a reauth link is outstanding."""
    try:
        if reauth_window_active():
            reauth_services.start()
        else:
            reauth_services.stop()
    except Exception:
        logger.exception("failed to sync reauth services")


def setup() -> None:
    sentry.init(dsn=Env.SENTRY_DSN, ignore_errors=[KeyboardInterrupt])
    setup_logging()


scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", minutes=15, next_run_time=datetime.datetime.now())
def main():
    try:
        ensure_token_valid()
    except ReauthRequired as e:
        logger.warning(f"skipping run, spotify reauth required: {e}")
        sync_reauth_services()
        return

    try:
        remind_if_expiry_near()
    except Exception:
        logger.exception("expiry reminder check failed")

    sync_reauth_services()

    srf = SRF()
    trending_now = TrendingNowCollection(srf=srf)
    top_100 = Top100Collection(srf=srf)
    night_out = NightOutCollection(srf=srf)

    for collection in [trending_now, top_100, night_out]:
        new_songs = collection.get_new_songs()
        if new_songs:
            collection.playlist.add_songs(new_songs)

        old_songs = collection.get_old_songs()
        if old_songs:
            collection.playlist.remove_songs(old_songs)

        time.sleep(1)


if __name__ == "__main__":
    setup()
    scheduler.start()
