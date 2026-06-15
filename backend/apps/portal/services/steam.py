from __future__ import annotations

import re
from urllib.parse import urlencode

import requests
from django.conf import settings

STEAM_OPENID_ENDPOINT = 'https://steamcommunity.com/openid/login'
STEAM_ID64_BASE = 76561197960265728


class SteamAuthError(RuntimeError):
    pass


def steam_id64_to_steam2(steam_id64: str) -> str:
    account_id = int(steam_id64) - STEAM_ID64_BASE
    auth_server = account_id % 2
    account_number = (account_id - auth_server) // 2
    return f'STEAM_1:{auth_server}:{account_number}'


def build_steam_login_url() -> str:
    """Build a Steam OpenID URL for dev and production.

    Steam requires a stable realm/return_to pair. For localhost it works only if
    the browser can reach steamcommunity.com and Steam accepts the exact return
    URL. In locked networks/VPN issues Steam may reset the connection; the
    project has an explicit DEV-login endpoint for local functional testing.
    """
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': settings.STEAM_RETURN_URL,
        'openid.realm': settings.STEAM_OPENID_REALM,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    return f'{STEAM_OPENID_ENDPOINT}?{urlencode(params)}'


def verify_steam_openid(query_params) -> str:
    data = query_params.copy()
    data['openid.mode'] = 'check_authentication'
    try:
        response = requests.post(STEAM_OPENID_ENDPOINT, data=data, timeout=settings.STEAM_REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SteamAuthError('Steam OpenID verification request failed.') from exc

    if 'is_valid:true' not in response.text:
        raise SteamAuthError('Steam OpenID did not validate the callback.')

    claimed_id = query_params.get('openid.claimed_id', '')
    match = re.search(r'https://steamcommunity\.com/openid/id/(\d+)', claimed_id)
    if not match:
        raise SteamAuthError('Steam OpenID callback does not contain SteamID64.')
    return match.group(1)


def fetch_steam_profile(steam_id64: str) -> dict[str, str]:
    if not settings.STEAM_API_KEY:
        return {
            'username': f'Steam {steam_id64[-6:]}',
            'avatar': '',
        }

    url = 'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    try:
        response = requests.get(
            url,
            params={'key': settings.STEAM_API_KEY, 'steamids': steam_id64},
            timeout=settings.STEAM_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SteamAuthError('Steam profile request failed.') from exc

    players = response.json().get('response', {}).get('players', [])
    if not players:
        return {'username': f'Steam {steam_id64[-6:]}', 'avatar': ''}

    player = players[0]
    return {
        'username': player.get('personaname') or f'Steam {steam_id64[-6:]}',
        'avatar': player.get('avatarfull') or player.get('avatarmedium') or '',
    }
