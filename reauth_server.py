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

import html
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote

from srfvirus_spotify.env import Env
from srfvirus_spotify.log import setup_logging
from srfvirus_spotify.reauth import authorize_url_for_state, exchange_code


logger = logging.getLogger(__name__)

CALLBACK_PATH = "/callback"
REAUTH_PREFIX = "/reauth/"


def _page(title: str, message: str, extra: str = "") -> bytes:
    return (
        f"<!doctype html><meta charset=utf-8><title>{title}</title>"
        f"<div style='font-family:system-ui;max-width:32rem;margin:4rem auto;text-align:center'>"
        f"<h1>{title}</h1><p>{message}</p>{extra}</div>"
    ).encode()


def _login_button(url: str) -> str:
    return (
        f"<a href='{html.escape(url, quote=True)}' "
        f"style='display:inline-block;margin-top:1rem;padding:.75rem 1.5rem;background:#1db954;"
        f"color:#fff;border-radius:2rem;text-decoration:none;font-weight:600'>Login to Spotify</a>"
    )


class Handler(BaseHTTPRequestHandler):

    def _respond(self, status: int, title: str, message: str, extra: str = "") -> None:
        body = _page(title, message, extra)
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self) -> None:
        self._respond(404, "Not Found", "")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == CALLBACK_PATH:
            return self._handle_callback(parsed)
        if parsed.path.startswith(REAUTH_PREFIX):
            return self._handle_reauth_page(parsed)
        return self._not_found()

    def _handle_reauth_page(self, parsed) -> None:
        # Intermediate page: a plain "Login to Spotify" button that links to the real OAuth URL.
        state = unquote(parsed.path[len(REAUTH_PREFIX) :])
        url = authorize_url_for_state(state)
        if url is None:
            return self._respond(
                400,
                "Link expired",
                "This re-authorization link is no longer valid. Please use the most recent email.",
            )
        self._respond(
            200,
            "Reconnect Spotify",
            "Click below to sign in and reconnect the automation.",
            _login_button(url),
        )

    def _handle_callback(self, parsed) -> None:
        params = parse_qs(parsed.query)
        error = params.get("error", [None])[0]
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]

        if error:
            return self._respond(400, "Authorization cancelled", f"Spotify reported: {error}")
        if not code:
            return self._not_found()

        try:
            result = exchange_code(code, state)
        except Exception:
            logger.exception("token exchange failed")
            return self._respond(500, "Error", "Token exchange failed. Please open the link again.")

        if result == "inactive":
            return self._not_found()
        if result == "bad_state":
            return self._respond(400, "Invalid request", "The state parameter does not match.")
        return self._respond(200, "Authorization successful", "You can close this window.")

    def log_message(self, *args) -> None:
        logger.info("%s - %s", self.address_string(), args[0] % args[1:])


def main() -> None:
    setup_logging()
    server = HTTPServer(("127.0.0.1", Env.REAUTH_PORT), Handler)
    logger.info(f"reauth callback server listening on 127.0.0.1:{Env.REAUTH_PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
