<p align="center">
    <div align="center">
        <img src="assets/srfvirus_icon.png" height="70px">
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <img src="assets/spotify_icon.png" height="70px">
    </div>
    <h1 align="center">SRF Virus – Spotify</h1>
    <p align="center">
        An application that automatically maintains the 
        <a href="https://open.spotify.com/playlist/6c6OWdem6i3ekL60K1SiKu">SRF Virus: Trending Now</a> 
        Spotify playlist.
    </p>
</p>

<br>

## About

The playlist consists of current trending songs that are played on the SRF Virus radio channel. 

The application adds songs to the playlist that are played at least three times within a week on SRF Virus. 
If a song is not played at least three times during the following week, it will be removed from the playlist.

## Application Flow

The application is scheduled to run every 15min and uses the SRGSSR Audio API to retrieve played songs
on the SRF Virus radio channel as well as the Spotify Web API to maintain the playlist itself.

The application follows these steps:

1. Get songs from the SRGSSR Audio API
2. Filter out songs received from the SRGSSR Audio API that are redundant from the last request
3. Search filtered songs on Spotify to get URI (song identifier)
4. Check if song is played enough and add/retain it in playlist, if check passed
5. Remove songs that aren't played enough from playlist

## Links

- [`SRF Virus: Trending Now` Spotify playlist](https://open.spotify.com/playlist/6c6OWdem6i3ekL60K1SiKu)
- [SRGSSR Audio API Docs](https://developer.srgssr.ch/api-catalog/srgssr-audio-0)
- [Spotify Web API Docs](https://developer.spotify.com/documentation/web-api)

## Disclaimer

This application is not affiliated with SRG SSR or Spotify and is not an official 
application of one of these companies. The application was developed independently and uses 
publicly available data in accordance with its terms of use.
