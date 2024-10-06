import logging

from srfvirus_spotify.spotify import add_song_to_playlist
from srfvirus_spotify.srf import SRF


logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.WARNING,
    handlers=[logging.FileHandler("./logs/logging.log"), logging.StreamHandler()],
)


def main() -> None:
    srf = SRF()
    new_songs = srf.get_new_songs()
    print(new_songs)

    # for new_song in new_songs:
    #     add_song_to_playlist(new_song)


if __name__ == "__main__":
    main()
