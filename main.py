import logging

from srfvirus_spotify.spotify import add_to_playlist, remove_from_playlist
from srfvirus_spotify.srf import SRF


logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.WARNING,
    handlers=[logging.FileHandler("./logs/logging.log"), logging.StreamHandler()],
)


def main() -> None:
    srf = SRF()

    # add new songs to playlist
    new_songs = srf.get_new_songs()
    add_to_playlist(new_songs)
    # remove old songs from playlist
    old_songs = srf.get_old_songs()
    remove_from_playlist(old_songs)


if __name__ == "__main__":
    main()
