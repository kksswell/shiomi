from django.contrib import admin

from .models import CaseReward, CaseSpin, GameServer, PurchaseRequest, Rule, ShopProduct, SteamUser


@admin.register(SteamUser)
class SteamUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'steam_id64', 'steam_id2', 'is_vip', 'vip_expires_at', 'is_server_admin',
        'admin_expires_at', 'credits', 'kills', 'deaths', 'last_login_at', 'updated_at'
    )
    list_filter = ('is_vip', 'is_server_admin')
    search_fields = ('username', 'steam_id64', 'steam_id2')
    readonly_fields = ('created_at', 'updated_at', 'first_login_at')
    fieldsets = (
        ('Steam', {'fields': ('steam_id64', 'steam_id2', 'username', 'avatar_url')}),
        ('Авторизация', {'fields': ('first_login_at', 'last_login_at')}),
        ('Привилегии', {'fields': ('is_vip', 'vip_expires_at', 'is_server_admin', 'admin_expires_at', 'credits')}),
        ('Статистика', {'fields': ('kills', 'deaths', 'headshots', 'level', 'last_spin_at')}),
        ('Служебное', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(GameServer)
class GameServerAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'port', 'mode', 'status_mode', 'max_players', 'is_active', 'sort_order')
    list_filter = ('status_mode', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'host', 'mode', 'description')


@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'period', 'product_type', 'duration_days', 'highlight', 'is_active', 'sort_order')
    list_filter = ('product_type', 'highlight', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(CaseReward)
class CaseRewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'rarity', 'chance', 'credits_delta', 'grants_vip', 'grants_admin', 'is_active', 'sort_order')
    list_filter = ('rarity', 'grants_vip', 'grants_admin', 'is_active')
    search_fields = ('title',)


@admin.register(CaseSpin)
class CaseSpinAdmin(admin.ModelAdmin):
    list_select_related = ('user', 'reward')
    date_hierarchy = 'created_at'
    list_display = ('user', 'reward', 'created_at')
    list_filter = ('reward__rarity', 'created_at')
    search_fields = ('user__username', 'user__steam_id64', 'reward__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.action(description='Одобрить выбранные заявки')
def mark_approved(modeladmin, request, queryset):
    queryset.update(status=PurchaseRequest.Status.APPROVED)


@admin.action(description='Отклонить выбранные заявки')
def mark_rejected(modeladmin, request, queryset):
    queryset.update(status=PurchaseRequest.Status.REJECTED)


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    actions = [mark_approved, mark_rejected]
    list_select_related = ('user', 'product')
    date_hierarchy = 'created_at'
    list_display = ('user', 'product', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'product', 'created_at')
    search_fields = ('user__username', 'user__steam_id64', 'product__title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
