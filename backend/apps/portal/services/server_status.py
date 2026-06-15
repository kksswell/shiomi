from __future__ import annotations

from datetime import datetime, timedelta
from threading import Lock
from typing import Any, TypedDict

from django.conf import settings
from django.utils import timezone


class ServerStatus(TypedDict):
    players: int
    maxPlayers: int
    online: bool
    host: str
    port: int
    updatedAt: str


_cache: dict[str, ServerStatus] = {}
_cache_until: dict[str, datetime] = {}
_cache_lock = Lock()


def _server_attr(server: Any | None, name: str, fallback: Any) -> Any:
    return getattr(server, name, fallback) if server is not None else fallback


def _server_key(server: Any | None) -> str:
    host = _server_attr(server, 'host', settings.GAME_SERVER_HOST)
    port = _server_attr(server, 'port', settings.GAME_SERVER_PORT)
    return f'{host}:{port}'


def _offline_status(now: datetime, server: Any | None = None) -> ServerStatus:
    return {
        'players': int(_server_attr(server, 'mock_players', 0) or 0),
        'maxPlayers': int(_server_attr(server, 'max_players', settings.GAME_SERVER_MAX_PLAYERS) or settings.GAME_SERVER_MAX_PLAYERS),
        'online': False,
        'host': str(_server_attr(server, 'host', settings.GAME_SERVER_HOST)),
        'port': int(_server_attr(server, 'port', settings.GAME_SERVER_PORT)),
        'updatedAt': now.isoformat(),
    }


def query_source_server(server: Any | None = None) -> ServerStatus:
    """Return cached CS2 server status without blocking the page for too long.

    A GameServer can use real Source Query (`status_mode=auto`) or safe mocked
    data (`status_mode=mock`) for local/VPS staging before the real CS2 server is reachable.
    """
    now = timezone.now()
    key = _server_key(server)
    mode = _server_attr(server, 'status_mode', 'auto')

    if mode == 'disabled':
        return _offline_status(now, server)

    if mode == 'mock':
        status = _offline_status(now, server)
        status['online'] = True
        return status

    if key in _cache and key in _cache_until and now < _cache_until[key]:
        return _cache[key]

    with _cache_lock:
        now = timezone.now()
        if key in _cache and key in _cache_until and now < _cache_until[key]:
            return _cache[key]

        status = _offline_status(now, server)
        timeout = max(0.2, float(settings.GAME_SERVER_TIMEOUT))

        try:
            import a2s

            info = a2s.info((status['host'], status['port']), timeout=timeout)
            status['players'] = int(getattr(info, 'player_count', 0) or 0)
            status['maxPlayers'] = int(getattr(info, 'max_players', status['maxPlayers']) or status['maxPlayers'])
            status['online'] = True
        except Exception:
            # Игровой сервер может быть недоступен, но сайт из-за этого не должен тормозить или падать.
            status['online'] = False

        _cache[key] = status
        _cache_until[key] = now + timedelta(seconds=max(5, int(settings.GAME_SERVER_CACHE_SECONDS)))
        return status
