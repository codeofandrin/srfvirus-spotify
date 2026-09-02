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

from __future__ import annotations

import hmac
import logging
import secrets
import time
from typing import Optional

from spotipy import SpotifyOAuth
from spotipy.exceptions import SpotifyOauthError

from .env import Env
from .cache_handler import TokenCacheFileHandler
from .errors import ReauthRequired
from .json_file import JSONFile
from .mailer import send_mail


logger = logging.getLogger(__name__)

SCOPES = "playlist-read-private,playlist-modify-private,playlist-modify-public"
TOKEN_PATH = "./.cache/.spotify_token"
REAUTH_PATH = "./.cache/.spotify_reauth.json"
AUTHORIZED_AT_KEY = "authorized_at"


def build_oauth(redirect_uri: Optional[str] = None) -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=Env.SPOTIFY_CLIENT_ID,
        client_secret=Env.SPOTIFY_CLIENT_SECRET,
        redirect_uri=redirect_uri or Env.SPOTIFY_REDIRECT_URI,
        scope=SCOPES,
        cache_handler=TokenCacheFileHandler(TOKEN_PATH, preserve_keys=(AUTHORIZED_AT_KEY,)),
        open_browser=False,
    )


def get_authorized_at() -> Optional[int]:
    return JSONFile(TOKEN_PATH).read().get(AUTHORIZED_AT_KEY)


def set_authorized_at(timestamp: float) -> None:
    json_file = JSONFile(TOKEN_PATH)
    data = json_file.read()
    data[AUTHORIZED_AT_KEY] = int(timestamp)
    json_file.write(data)


class ReauthState:
    """Short-lived window during which the callback server accepts a Spotify redirect."""

    def __init__(
        self,
        state: str = "",
        expires_at: float = 0.0,
        reminders_sent: int = 0,
        last_mail_at: float = 0.0,
    ):
        self.state = state
        self.expires_at = expires_at
        self.reminders_sent = reminders_sent
        self.last_mail_at = last_mail_at

    @classmethod
    def load(cls) -> "ReauthState":
        data = JSONFile(REAUTH_PATH).read()
        return cls(**{k: v for k, v in data.items() if k in cls().__dict__})

    def save(self) -> None:
        JSONFile(REAUTH_PATH).write(self.__dict__)

    def clear(self) -> None:
        JSONFile(REAUTH_PATH).write({})

    def active(self, now: Optional[float] = None) -> bool:
        return bool(self.state) and (now or time.time()) < self.expires_at


def arm_and_notify(reason: str) -> None:
    """Ensure a reauth window is open and a login link has been mailed.

    At most one mail per ``REAUTH_MAIL_INTERVAL_HOURS``; within that interval the
    existing link stays valid and nothing is sent. Every mail that does go out
    carries a fresh magic link, which invalidates the previous one.
    """
    st = ReauthState.load()
    now = time.time()

    if st.last_mail_at and now - st.last_mail_at < Env.REAUTH_MAIL_INTERVAL_HOURS * 3600:
        logger.info(
            "reauth mail already sent within the last %sh; keeping the current link",
            Env.REAUTH_MAIL_INTERVAL_HOURS,
        )
        return

    state = secrets.token_urlsafe(32)
    expires_at = now + Env.REAUTH_WINDOW_HOURS * 3600
    # Link to the intermediate page, not the raw Spotify URL; spam filters dislike long third-party links.
    url = f"{Env.REAUTH_PAGE_BASE_URL}/reauth/{state}"

    reminder = st.reminders_sent + 1
    subject = "srfvirus-spotify: Your token needs a refresh"
    body = (
        f"Hi Andrin,\n\n"
        f"Update for your srfvirus-spotify automation. The Spotify token needs a refresh 🔄.\n"
        f"Reason: {reason}\n\n"
        f"If you have a moment, you can refresh it here:\n{url}\n\n"
        f"The link is only valid for {Env.REAUTH_WINDOW_HOURS}h and replaces any earlier link."
        f"After that I'll send you a new one (max. every {Env.REAUTH_MAIL_INTERVAL_HOURS}h).\n\n"
        f"Best Regards,\n"
        f"Your srfvirus-spotify Automation\n\n"
        f"This is an automated message."
    )
    send_mail(subject, body)

    st.state = state
    st.expires_at = expires_at
    st.reminders_sent = reminder
    st.last_mail_at = now
    st.save()
    logger.info(f"armed reauth window (reminder {reminder}); link valid {Env.REAUTH_WINDOW_HOURS}h")


def _require_reauth(reason: str, *, discard_token: bool = False) -> ReauthRequired:
    """Discard the dead token if asked, open a reauth window + mail the link, return the error to raise."""
    if discard_token:
        JSONFile(TOKEN_PATH).write({})
    try:
        arm_and_notify(reason)
    except Exception:
        logger.exception("failed to send reauth mail")
    return ReauthRequired(reason)


def ensure_token_valid() -> None:
    """Proactively refresh the access token. Raises ReauthRequired on an expired refresh token."""
    oauth = build_oauth()
    token_info = oauth.cache_handler.get_cached_token()
    if not token_info or "refresh_token" not in token_info:
        raise _require_reauth("no cached spotify token")

    try:
        refreshed = oauth.validate_token(token_info)
    except SpotifyOauthError as e:
        if getattr(e, "error", None) != "invalid_grant":
            raise
        logger.warning("spotify refresh token rejected (invalid_grant); discarding and notifying")
        raise _require_reauth("invalid_grant on token refresh", discard_token=True) from e

    if refreshed is None:
        raise _require_reauth("cached token no longer valid")


def remind_if_expiry_near() -> None:
    """Mail a login link before the ~180-day refresh-token expiry.

    Runs on every loop tick while the token is still valid; the actual mail is
    rate-limited by ``arm_and_notify``.
    """
    authorized_at = get_authorized_at()
    if authorized_at is None:
        logger.warning("no authorized_at cached; arming reauth")
        arm_and_notify("no authorization timestamp cached")
        return

    age_days = (time.time() - authorized_at) / 86400
    if age_days < Env.REAUTH_REMINDER_DAYS:
        return
    logger.info(f"refresh token age {age_days:.1f}d >= {Env.REAUTH_REMINDER_DAYS}d; arming reauth")
    arm_and_notify(f"refresh token is {age_days:.0f} days old (expires after ~180 days)")


def reauth_window_active() -> bool:
    """True while a reauth link is outstanding (drives the on-demand tunnel + server)."""
    return ReauthState.load().active()


def authorize_url_for_state(state: Optional[str]) -> Optional[str]:
    """Called by the intermediate reauth page. Returns the Spotify authorize URL for a
    still-valid state, or None if the window is closed or the state does not match."""
    st = ReauthState.load()
    if not st.active():
        return None
    if not (state and hmac.compare_digest(state, st.state)):
        return None
    return build_oauth().get_authorize_url(state=state)


def exchange_code(code: str, state: Optional[str]) -> str:
    """Called by the callback server. Returns 'ok' | 'inactive' | 'bad_state'."""
    st = ReauthState.load()
    if not st.active():
        return "inactive"
    if not (state and hmac.compare_digest(state, st.state)):
        return "bad_state"

    build_oauth().get_access_token(code=code, as_dict=False, check_cache=False)
    set_authorized_at(time.time())
    st.clear()
    logger.info("reauth complete; new refresh token stored, window closed")
    return "ok"
