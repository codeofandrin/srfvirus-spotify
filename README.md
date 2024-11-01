<p align="center">
    <div align="center">
        <img src="assets/srfvirus_icon.png" height="70px">
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <img src="assets/spotify_icon.png" height="70px">
    </div>
    <h1 align="center">SRF Virus – Spotify</h1>
    <p align="center">
        An application that automatically maintains multiple SRF Virus playlists on Spotify.
    </p>
</p>

<br>

## About

There are following playlists this application maintains:
- [SRF Virus: Trending Now](https://open.spotify.com/playlist/6c6OWdem6i3ekL60K1SiKu)
- [SRF Virus: Top 100](https://open.spotify.com/playlist/0LeU6iPYgFSEJKIDpzOo3k)

Read more below.

### SRF Virus: Trending Now
This playlist consists of current trending songs that are played on the SRF Virus radio channel. 

The application adds songs to the playlist that are played at least three times within a week on SRF Virus. 
If a song is not played at least three times during the following week, it will be removed from the playlist.

### Top 100
This playlist consists of current top 100 most played songs on the SRF Virus radio channel.

The application increments the count of a song every time it's played. Then it's sorted by counts
and the songs in the top 100 that aren't in the playlist yet are added. Every song beyond the top 100
is removed, if it's in the playlist.

## Application Flow

The application is scheduled to run every 15min and uses the SRGSSR Audio API to retrieve played songs
on the SRF Virus radio channel as well as the Spotify Web API to maintain the playlist itself.

The application follows these steps:

1. Get songs from the SRGSSR Audio API
2. Filter out songs received from the SRGSSR Audio API that are redundant from the last request
3. Search filtered songs on Spotify to get URI (song identifier)
4. Add songs if they meet the criteria for the respective playlist
5. Remove songs that don't meet the criteria anymore

## Additional Links

- [SRGSSR Audio API Docs](https://developer.srgssr.ch/api-catalog/srgssr-audio-0)
- [Spotify Web API Docs](https://developer.spotify.com/documentation/web-api)

## Disclaimer

This application is not affiliated with SRG SSR or Spotify and is not an official 
application of one of these companies. The application was developed independently and uses 
publicly available data in accordance with its terms of use.
