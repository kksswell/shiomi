from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CaseReward, CaseSpin, GameServer, PurchaseRequest, Rule, ShopProduct, SteamUser
from .serializers import (
    CaseRewardSerializer,
    GameServerSerializer,
    PurchaseRequestSerializer,
    RuleSerializer,
    ShopProductSerializer,
    SteamUserProfileSerializer,
)
from .services.server_status import query_source_server
from .services.steam import SteamAuthError, build_steam_login_url, fetch_steam_profile, steam_id64_to_steam2, verify_steam_openid


def _current_steam_user(request) -> SteamUser | None:
    steam_user_id = request.session.get('steam_user_id')
    if not steam_user_id:
        return None
    try:
        return SteamUser.objects.get(id=steam_user_id)
    except SteamUser.DoesNotExist:
        request.session.flush()
        return None


def _frontend_redirect(query: str = ''):
    separator = '&' if '?' in settings.FRONTEND_URL else '?'
    return redirect(f'{settings.FRONTEND_URL}{separator}{query}' if query else settings.FRONTEND_URL)




def _is_local_request(request) -> bool:
    host = request.get_host().split(':', 1)[0].lower()
    return host in {'localhost', '127.0.0.1', '0.0.0.0'}


def _effective_login_path(request=None) -> str:
    if settings.STEAM_DEV_LOGIN_ENABLED and (request is None or _is_local_request(request)):
        return '/api/auth/steam/dev/'
    return '/api/auth/steam/'

def _auth_config(request=None) -> dict[str, object]:
    return {
        'devLoginEnabled': bool(settings.STEAM_DEV_LOGIN_ENABLED),
        'steamConfigured': bool(settings.STEAM_OPENID_REALM and settings.STEAM_RETURN_URL),
        'steamRealm': settings.STEAM_OPENID_REALM,
        'steamReturnUrl': settings.STEAM_RETURN_URL,
        'recommendedLoginUrl': _effective_login_path(request),
        'realSteamLoginUrl': '/api/auth/steam/',
        'devLoginUrl': '/api/auth/steam/dev/',
    }


def _login_user(request, steam_id64: str, username: str, avatar_url: str = '') -> SteamUser:
    now = timezone.now()
    user, created = SteamUser.objects.update_or_create(
        steam_id64=steam_id64,
        defaults={
            'steam_id2': steam_id64_to_steam2(steam_id64),
            'username': username,
            'avatar_url': avatar_url,
            'last_login_at': now,
        },
    )
    if created and not user.first_login_at:
        user.first_login_at = now
        user.save(update_fields=['first_login_at'])
    request.session['steam_user_id'] = user.id
    request.session.modified = True
    return user


def _active_servers():
    return GameServer.objects.filter(is_active=True).order_by('sort_order', 'id')


def _server_payload(request) -> tuple[list[dict], dict]:
    servers = list(_active_servers())
    if not servers:
        status_payload = query_source_server()
        return [], status_payload

    serialized_servers = []
    total_players = 0
    any_online = False
    latest_status = None
    for server in servers:
        status_payload = query_source_server(server)
        latest_status = latest_status or status_payload
        total_players += status_payload['players']
        any_online = any_online or status_payload['online']
        server.players = status_payload['players']
        server.online = status_payload['online']
        server.updatedAt = status_payload['updatedAt']
        serialized = GameServerSerializer(server, context={'request': request}).data
        serialized_servers.append(serialized)

    first = latest_status or query_source_server()
    aggregate = {
        **first,
        'players': total_players,
        'online': any_online,
    }
    return serialized_servers, aggregate


@api_view(['GET'])
def server_status(request):
    servers, aggregate = _server_payload(request)
    if servers:
        aggregate['servers'] = servers
    return Response(aggregate)


@api_view(['GET'])
def servers(request):
    server_items, aggregate = _server_payload(request)
    return Response({'servers': server_items, 'totalOnline': aggregate['players'], 'anyOnline': aggregate['online']})


@api_view(['GET'])
def profile(request):
    user = _current_steam_user(request)
    if not user:
        return Response({'detail': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(SteamUserProfileSerializer(user).data)


@api_view(['GET'])
def steam_login(request):
    # На localhost Steam OpenID часто отдаёт Access Denied/connection reset из-за
    # политики steamcommunity/Akamai и нестабильных сетей. Поэтому в локальной
    # среде при включённом STEAM_DEV_LOGIN_ENABLED обычная кнопка входа ведёт
    # в безопасный dev-login, а production с STEAM_DEV_LOGIN_ENABLED=false
    # использует настоящий Steam OpenID.
    if settings.STEAM_DEV_LOGIN_ENABLED and _is_local_request(request):
        return steam_dev_login(request)
    return redirect(build_steam_login_url())


@api_view(['GET'])
def steam_return(request):
    try:
        steam_id64 = verify_steam_openid(request.GET)
        steam_profile = fetch_steam_profile(steam_id64)
        _login_user(request, steam_id64, steam_profile['username'], steam_profile.get('avatar', ''))
        return _frontend_redirect('auth=success')
    except (SteamAuthError, ValueError):
        return _frontend_redirect('auth=failed')
    except Exception:
        return _frontend_redirect('auth=server-error')


@api_view(['GET'])
def steam_dev_login(request):
    if not settings.STEAM_DEV_LOGIN_ENABLED:
        return Response({'detail': 'DEV-вход отключён'}, status=status.HTTP_404_NOT_FOUND)
    _login_user(
        request,
        settings.STEAM_DEV_STEAM_ID64,
        settings.STEAM_DEV_USERNAME,
        '',
    )
    return _frontend_redirect('auth=success')


@api_view(['GET', 'POST'])
def logout(request):
    request.session.flush()
    if request.method == 'GET':
        return _frontend_redirect('logout=success')
    return Response({'status': 'ok'})


@api_view(['GET'])
def bootstrap(request):
    """Single fast endpoint for the first page render."""
    user = _current_steam_user(request)
    server_items, aggregate_status = _server_payload(request)
    products = ShopProduct.objects.filter(is_active=True).only(
        'id', 'title', 'slug', 'description', 'price', 'period', 'product_type', 'duration_days', 'icon', 'badge', 'highlight'
    )
    active_rules = Rule.objects.filter(is_active=True).only('id', 'title', 'description', 'points')
    active_rewards = CaseReward.objects.filter(is_active=True).only('id', 'title', 'rarity', 'icon', 'chance')

    return Response(
        {
            'profile': SteamUserProfileSerializer(user).data if user else None,
            'server': aggregate_status,
            'servers': server_items,
            'products': ShopProductSerializer(products, many=True).data,
            'rules': RuleSerializer(active_rules, many=True).data,
            'rewards': CaseRewardSerializer(active_rewards, many=True).data,
            'auth': _auth_config(request),
        }
    )


@api_view(['GET'])
def shop_products(_request):
    products = ShopProduct.objects.filter(is_active=True).only(
        'id', 'title', 'slug', 'description', 'price', 'period', 'product_type', 'duration_days', 'icon', 'badge', 'highlight'
    )
    return Response(ShopProductSerializer(products, many=True).data)


@api_view(['POST'])
def create_purchase(request):
    user = _current_steam_user(request)
    if not user:
        return Response({'detail': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

    product_id = request.data.get('productId') or request.data.get('product_id')
    if not product_id:
        return Response({'detail': 'Не передан товар'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return Response({'detail': 'Некорректный товар'}, status=status.HTTP_400_BAD_REQUEST)

    product = get_object_or_404(ShopProduct.objects.filter(is_active=True), id=product_id)
    try:
        purchase, created = PurchaseRequest.objects.select_related('product').get_or_create(
            user=user,
            product=product,
            status=PurchaseRequest.Status.PENDING,
        )
    except IntegrityError:
        purchase = PurchaseRequest.objects.select_related('product').get(
            user=user,
            product=product,
            status=PurchaseRequest.Status.PENDING,
        )
        created = False
    return Response(
        {
            'detail': 'Заявка создана. Администратор сможет обработать её в Django Admin.'
            if created
            else 'У вас уже есть активная заявка на этот товар.',
            'purchase': PurchaseRequestSerializer(purchase).data,
        },
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(['GET'])
def rules(_request):
    active_rules = Rule.objects.filter(is_active=True).only('id', 'title', 'description', 'points')
    return Response(RuleSerializer(active_rules, many=True).data)


@api_view(['GET'])
def rewards(_request):
    active_rewards = CaseReward.objects.filter(is_active=True).only('id', 'title', 'rarity', 'icon', 'chance')
    return Response(CaseRewardSerializer(active_rewards, many=True).data)


@api_view(['POST'])
def spin_case(request):
    user = _current_steam_user(request)
    if not user:
        return Response({'detail': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

    now = timezone.now()
    with transaction.atomic():
        user = SteamUser.objects.select_for_update().get(pk=user.pk)
        if user.last_spin_at and now - user.last_spin_at < timedelta(hours=24):
            return Response({'detail': 'Бонус уже получен за последние 24 часа'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        rewards_queryset = list(CaseReward.objects.filter(is_active=True).order_by('sort_order', 'id'))
        if not rewards_queryset:
            return Response({'detail': 'Награды колеса не настроены'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        reward = _weighted_reward(rewards_queryset)
        user.credits += reward.credits_delta
        user.last_spin_at = now
        if reward.grants_vip:
            user.is_vip = True
            user.vip_expires_at = max(user.vip_expires_at or now, now) + timedelta(days=3)
        if reward.grants_admin:
            user.is_server_admin = True
            user.admin_expires_at = max(user.admin_expires_at or now, now) + timedelta(days=3)
        user.save(update_fields=['credits', 'last_spin_at', 'is_vip', 'is_server_admin', 'vip_expires_at', 'admin_expires_at', 'updated_at'])
        CaseSpin.objects.create(user=user, reward=reward)

    return Response(
        {
            'reward': CaseRewardSerializer(reward).data,
            'credits': user.credits,
            'lastSpin': user.last_spin_at.isoformat(),
            'nextSpinAvailableAt': (user.last_spin_at + timedelta(hours=24)).isoformat(),
        }
    )


def _weighted_reward(rewards: list[CaseReward]) -> CaseReward:
    total = sum(Decimal(reward.chance) for reward in rewards)
    if total <= 0:
        return random.choice(rewards)

    cursor = Decimal(str(random.uniform(0, float(total))))
    for reward in rewards:
        cursor -= Decimal(reward.chance)
        if cursor <= 0:
            return reward
    return rewards[-1]
