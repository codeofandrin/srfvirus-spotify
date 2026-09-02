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

import logging
import os
import signal
import subprocess
import sys
import time
from typing import Dict, List, Optional

from .env import Env
from .json_file import JSONFile


logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = "./.cache/.reauth_services.json"
SERVICES_LOG = "./logs/reauth_services.log"

TUNNEL_KEY = "cloudflared_pid"
SERVER_KEY = "server_pid"

_TERM_WAIT_STEPS = 20
_TERM_WAIT_INTERVAL = 0.25

_procs: Dict[str, subprocess.Popen] = {}


def _pid_alive(pid: Optional[int]) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _alive(key: str, pid: Optional[int]) -> bool:
    proc = _procs.get(key)
    if proc is not None:
        return proc.poll() is None  # poll() also reaps the child once it exits
    return _pid_alive(pid)


def _spawn(args: List[str]) -> subprocess.Popen:
    os.makedirs(os.path.dirname(SERVICES_LOG), exist_ok=True)
    log_fd = open(SERVICES_LOG, "a")
    try:
        return subprocess.Popen(
            args,
            cwd=BASE_DIR,
            stdout=log_fd,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    finally:
        log_fd.close()  # the child keeps its own dup of the fd


def _terminate(key: str, pid: Optional[int]) -> None:
    proc = _procs.pop(key, None)
    if proc is not None:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=_TERM_WAIT_STEPS * _TERM_WAIT_INTERVAL)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=_TERM_WAIT_STEPS * _TERM_WAIT_INTERVAL)
        return

    if not _pid_alive(pid):
        return
    try:
        os.kill(pid, signal.SIGTERM)  # type: ignore can't be None here
    except ProcessLookupError:
        return
    for _ in range(_TERM_WAIT_STEPS):
        time.sleep(_TERM_WAIT_INTERVAL)
        if not _pid_alive(pid):
            return
    try:
        os.kill(pid, signal.SIGKILL)  # type: ignore can't be None here
    except ProcessLookupError:
        pass


def running() -> bool:
    """True only if both the tunnel and the callback server are alive."""
    state = JSONFile(STATE_PATH).read()
    return _alive(TUNNEL_KEY, state.get(TUNNEL_KEY)) and _alive(SERVER_KEY, state.get(SERVER_KEY))


def start() -> None:
    """Bring up the cloudflared tunnel and the callback server."""
    state = JSONFile(STATE_PATH).read()
    tunnel_pid = state.get(TUNNEL_KEY)
    server_pid = state.get(SERVER_KEY)

    if not _alive(TUNNEL_KEY, tunnel_pid):
        if not Env.CLOUDFLARE_TUNNEL_TOKEN:
            raise RuntimeError("CLOUDFLARE_TUNNEL_TOKEN not set; cannot open reauth tunnel")
        proc = _spawn(
            [
                "/usr/local/bin/cloudflared",
                "tunnel",
                "--no-autoupdate",
                "run",
                "--token",
                Env.CLOUDFLARE_TUNNEL_TOKEN,
            ]
        )
        _procs[TUNNEL_KEY] = proc
        tunnel_pid = proc.pid
        logger.info(f"started cloudflared tunnel (pid {tunnel_pid})")

    if not _alive(SERVER_KEY, server_pid):
        proc = _spawn([sys.executable, os.path.join(BASE_DIR, "reauth_server.py")])
        _procs[SERVER_KEY] = proc
        server_pid = proc.pid
        logger.info(f"started reauth callback server (pid {server_pid})")

    JSONFile(STATE_PATH).write({TUNNEL_KEY: tunnel_pid, SERVER_KEY: server_pid})


def stop() -> None:
    """Tear down the callback server and the tunnel."""
    state = JSONFile(STATE_PATH).read()
    if not (_procs or state):
        return

    _terminate(SERVER_KEY, state.get(SERVER_KEY))
    _terminate(TUNNEL_KEY, state.get(TUNNEL_KEY))
    if state:
        JSONFile(STATE_PATH).write({})
    logger.info("stopped reauth tunnel + callback server")
