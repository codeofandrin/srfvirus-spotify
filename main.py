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

import logging
import datetime
import os
import time

import sentry_sdk as sentry
from apscheduler.schedulers.blocking import BlockingScheduler

from srfvirus_spotify.srf import SRF, TrendingNowCollection, Top100Collection, NightOutCollection
from srfvirus_spotify.env import Env


logger = logging.getLogger(__name__)


def setup() -> None:
    ignore_errors = [KeyboardInterrupt]
    sentry.init(
        dsn=Env.SENTRY_DSN,
        ignore_errors=ignore_errors,
    )

    log_path = "./logs/logging.log"
    if not os.path.exists(log_path):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%d.%m.%y %H:%M:%S %Z",
        level=logging.INFO,
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )


scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", minutes=15, next_run_time=datetime.datetime.now())
def main():
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
