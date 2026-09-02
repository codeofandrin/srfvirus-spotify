<p align="center">
    <div align="center">
        <img src="assets/srfvirus_icon.png" width="70px">
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <img src="assets/spotify_icon.png" width="70px">
    </div>
    <h1 align="center">SRF Virus – Spotify</h1>
    <p align="center">
        A script that automatically maintains multiple SRF Virus playlists on Spotify.
    </p>
</p>

<br>

## About

There are following playlists this application maintains:
- [SRF Virus: Trending Now](https://open.spotify.com/playlist/6c6OWdem6i3ekL60K1SiKu)
- [SRF Virus: Top 100](https://open.spotify.com/playlist/0LeU6iPYgFSEJKIDpzOo3k)
- [SRF Virus: Night Out](https://open.spotify.com/playlist/4By2u7VJKKvSwVRXQZ1UnN)

Read more below.

### SRF Virus: Trending Now
This playlist contains currently trending songs played on the SRF Virus radio channel.

The application adds songs to the playlist once they have been played at least three times within one week.
If a song is not played at least three times during the following week, it is removed from the playlist.

### SRF Virus: Top 100
This playlist contains the current top 100 most-played songs on the SRF Virus radio channel.

The application increments a song’s play count each time it is played. The songs are then sorted by play count.
Songs that enter the top 100 and are not yet in the playlist are added. Songs that fall below the top 100 are removed from the playlist.
Additionally, if a song has not been played for 10 days, it is removed as well.

### SRF Virus: Night Out
This playlist contains songs played on the SRF Virus radio channel during the “Night Out” program.
The program airs on Saturdays between 20:00 and 23:59 (CET).

The application adds songs to the playlist once they have been played at least once within three weeks.
If a song is not played again within the following three weeks, it is removed from the playlist.

## Application Flow

The application runs every 15 minutes. It uses the SRGSSR Audio API to retrieve songs played on the SRF Virus radio channel and the Spotify Web API to manage the playlists.

The application performs the following steps:
	1.	Retrieve songs from the SRGSSR Audio API
	2.	Filter out songs that are redundant from the previous request
	3.	Search the remaining songs on Spotify to obtain the URI (song identifier)
	4.	Add songs that meet the criteria for the respective playlist
	5.	Remove songs that no longer meet the criteria

## Reauthorization

Spotify refresh tokens expire 6 months after the original user authorization (enforced for existing apps since 20 July 2026). 
On expiry the token endpoint returns `400 invalid_grant` and the user must sign in again. The reauth flow sends an email
with a link to re-authorize and refresh the token.

### One-time setup

1. **Cloudflare Zero Trust**: create a tunnel, add a public hostname `<optional-subdomain>.<your-domain>` and point 
to `http://localhost:8888`. Cloudlfare creates the DNS record automatically. Copy the tunnel token.
2. **Spotify Developer Dashboard**: add redirect URI
`https://<your-domain>/callback`.
3. **Resend**: verify the sender domain and create an API key.
4. **Server `.env`**: Set env variables (see `.env.example`)
5. **Install cloudflared**: See Cloudflare documentation / walk-through. However **do not** run `cloudflared service install`.
`reauth_services.py` starts it token-based only when a reauth is pending.
7. On the first tick `remind_if_expiry_near()` finds no `authorized_at` and sends
   the first reauth mail. Everything runs automatically after that.

## Tech Stack
- Python 3.9+
- spotipy (API Wrapper for the Spotify Web API)
- cloudflared (on-demand tunnel for reauth server)
- Resend (reminder mails)

## Additional Links

- [SRGSSR Audio API Docs](https://developer.srgssr.ch/en/apis/srgssr-audio)
- [Spotify Web API Docs](https://developer.spotify.com/documentation/web-api)

## Disclaimer

This application is not affiliated with SRG SSR or Spotify and is not an official 
application of one of these companies. The application was developed independently and uses 
publicly available data in accordance with its terms of use.

## Copyright

Copyright (c) codeofandrin 

This source code is licensed under the MIT license found in the
[LICENSE](LICENSE) file in the root directory of this source tree.
