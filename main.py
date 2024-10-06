import logging
import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from srfvirus_spotify.spotify import add_to_playlist, remove_from_playlist
from srfvirus_spotify.srf import SRF


logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler("./logs/logging.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", minutes=20, next_run_time=datetime.datetime.now())
def main():
    srf = SRF()

    # add new songs to playlist
    logger.info("add new songs")
    new_songs = srf.get_new_songs()
    add_to_playlist(new_songs)

    # remove old songs from playlist
    logger.info("remove old songs")
    old_songs = srf.get_old_songs()
    remove_from_playlist(old_songs)


if __name__ == "__main__":
    scheduler.start()
