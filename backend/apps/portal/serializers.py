from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import CaseReward, GameServer, PurchaseRequest, Rule, ShopProduct, SteamUser


class SteamUserProfileSerializer(serializers.ModelSerializer):
    steamId = serializers.CharField(source='steam_id64')
    steamId2 = serializers.CharField(source='steam_id2')
    username = serializers.CharField()
    avatar = serializers.CharField(source='avatar_url')
    roles = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    privileges = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at')
    firstLoginAt = serializers.DateTimeField(source='first_login_at')
    lastLoginAt = serializers.DateTimeField(source='last_login_at', allow_null=True)
    lastSpin = serializers.DateTimeField(source='last_spin_at', allow_null=True)
    nextSpinAvailableAt = serializers.SerializerMethodField()

    class Meta:
        model = SteamUser
        fields = (
            'steamId',
            'steamId2',
            'username',
            'avatar',
            'roles',
            'stats',
            'privileges',
            'createdAt',
            'firstLoginAt',
            'lastLoginAt',
            'lastSpin',
            'nextSpinAvailableAt',
        )

    def get_nextSpinAvailableAt(self, obj: SteamUser) -> str | None:
        if not obj.last_spin_at:
            return None
        next_at = obj.last_spin_at + timedelta(hours=24)
        return next_at.isoformat() if next_at > timezone.now() else None

    def get_roles(self, obj: SteamUser) -> dict[str, bool]:
        return {'admin': obj.active_admin, 'vip': obj.active_vip}

    def get_privileges(self, obj: SteamUser) -> list[dict[str, str | bool | None]]:
        items: list[dict[str, str | bool | None]] = []
        if obj.is_vip:
            items.append({'title': 'VIP', 'active': obj.active_vip, 'expiresAt': obj.vip_expires_at.isoformat() if obj.vip_expires_at else None})
        if obj.is_server_admin:
            items.append({'title': 'ADMIN', 'active': obj.active_admin, 'expiresAt': obj.admin_expires_at.isoformat() if obj.admin_expires_at else None})
        if not items:
            items.append({'title': 'Игрок', 'active': True, 'expiresAt': None})
        return items

    def get_stats(self, obj: SteamUser) -> dict[str, int]:
        return {
            'kills': obj.kills,
            'deaths': obj.deaths,
            'headshots': obj.headshots,
            'level': obj.level,
            'points': obj.credits,
        }


class GameServerSerializer(serializers.ModelSerializer):
    address = serializers.CharField(read_only=True)
    imageUrl = serializers.SerializerMethodField()
    players = serializers.IntegerField(read_only=True)
    maxPlayers = serializers.IntegerField(source='max_players')
    online = serializers.BooleanField(read_only=True)
    updatedAt = serializers.CharField(read_only=True)
    mapName = serializers.CharField(source='map_name')
    connectUrl = serializers.CharField(source='connect_url')

    class Meta:
        model = GameServer
        fields = (
            'id',
            'title',
            'slug',
            'mode',
            'mapName',
            'description',
            'host',
            'port',
            'address',
            'players',
            'maxPlayers',
            'online',
            'updatedAt',
            'imageUrl',
            'connectUrl',
        )

    def get_imageUrl(self, obj: GameServer) -> str:
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return ''


class ShopProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    productType = serializers.CharField(source='product_type')
    durationDays = serializers.IntegerField(source='duration_days')

    class Meta:
        model = ShopProduct
        fields = ('id', 'title', 'slug', 'description', 'price', 'period', 'productType', 'durationDays', 'icon', 'badge', 'highlight')

    def get_price(self, obj: ShopProduct) -> str:
        return str(int(obj.price))


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ('id', 'title', 'description', 'points')


class CaseRewardSerializer(serializers.ModelSerializer):
    chance = serializers.SerializerMethodField()

    class Meta:
        model = CaseReward
        fields = ('id', 'title', 'rarity', 'icon', 'chance')

    def get_chance(self, obj: CaseReward) -> float:
        return float(obj.chance)


class PurchaseRequestSerializer(serializers.ModelSerializer):
    productTitle = serializers.CharField(source='product.title', read_only=True)
    productType = serializers.CharField(source='product.product_type', read_only=True)
    statusLabel = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = ('id', 'productTitle', 'productType', 'status', 'statusLabel', 'created_at')
