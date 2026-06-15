from __future__ import annotations

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SteamUser(TimeStampedModel):
    steam_id64 = models.CharField('SteamID64', max_length=32, unique=True)
    steam_id2 = models.CharField('SteamID2', max_length=32, blank=True)
    username = models.CharField('Никнейм', max_length=255)
    avatar_url = models.URLField('Аватар', blank=True)
    first_login_at = models.DateTimeField('Первый вход', default=timezone.now)
    last_login_at = models.DateTimeField('Последний вход', null=True, blank=True)
    is_vip = models.BooleanField('VIP', default=False)
    is_server_admin = models.BooleanField('Админ сервера', default=False)
    vip_expires_at = models.DateTimeField('VIP до', null=True, blank=True)
    admin_expires_at = models.DateTimeField('Админка до', null=True, blank=True)
    credits = models.PositiveIntegerField('Кредиты', default=0)
    kills = models.PositiveIntegerField('Убийства', default=0)
    deaths = models.PositiveIntegerField('Смерти', default=0)
    headshots = models.PositiveIntegerField('Headshots', default=0)
    level = models.PositiveIntegerField('Уровень', default=1)
    last_spin_at = models.DateTimeField('Последнее открытие бонуса', null=True, blank=True)

    class Meta:
        verbose_name = 'Steam пользователь'
        verbose_name_plural = 'Steam пользователи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='steam_user_created_idx'),
            models.Index(fields=['steam_id64'], name='steam_user_id64_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.username} ({self.steam_id64})'

    @property
    def active_vip(self) -> bool:
        return self.is_vip and (self.vip_expires_at is None or self.vip_expires_at > timezone.now())

    @property
    def active_admin(self) -> bool:
        return self.is_server_admin and (self.admin_expires_at is None or self.admin_expires_at > timezone.now())


class GameServer(TimeStampedModel):
    class StatusMode(models.TextChoices):
        AUTO = 'auto', 'Авто через Source Query'
        MOCK = 'mock', 'Моковые данные'
        DISABLED = 'disabled', 'Отключён'

    title = models.CharField('Название', max_length=120, default='PUBLIC')
    slug = models.SlugField('Slug', max_length=140, unique=True, default='public')
    mode = models.CharField('Режим', max_length=120, default='Соревновательный режим')
    map_name = models.CharField('Карта/описание', max_length=120, blank=True, default='CS2 Community')
    description = models.TextField('Описание', blank=True, default='Тёмный CS2-сервер SHIOMI с премиальной атмосферой.')
    host = models.CharField('Host/IP', max_length=120, default='170.168.115.48')
    port = models.PositiveIntegerField('Port', default=27115)
    max_players = models.PositiveIntegerField('Максимум игроков', default=24)
    mock_players = models.PositiveIntegerField('Моковый онлайн', default=0)
    status_mode = models.CharField('Источник статуса', max_length=20, choices=StatusMode.choices, default=StatusMode.AUTO)
    image = models.ImageField('Фон карточки', upload_to='servers/', blank=True)
    connect_url = models.CharField('Ссылка подключения', max_length=255, blank=True)
    sort_order = models.PositiveIntegerField('Сортировка', default=100)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Игровой сервер'
        verbose_name_plural = 'Игровые серверы'
        ordering = ['sort_order', 'id']
        indexes = [models.Index(fields=['is_active', 'sort_order'], name='server_active_sort_idx')]

    def __str__(self) -> str:
        return f'{self.title} {self.host}:{self.port}'

    @property
    def address(self) -> str:
        return f'{self.host}:{self.port}'


class ShopProduct(TimeStampedModel):
    class Highlight(models.TextChoices):
        DEFAULT = 'default', 'Обычный'
        PREMIUM = 'premium', 'Premium'
        SHIOMI = 'shiomi', 'ShioMI'

    class ProductType(models.TextChoices):
        VIP = 'vip', 'VIP'
        PREMIUM = 'premium', 'Premium VIP'
        ADMIN = 'admin', 'Админка'
        STATUS = 'status', 'SHIOMI Status'
        CREDITS = 'credits', 'Кредиты'
        OTHER = 'other', 'Другое'

    title = models.CharField('Название', max_length=120)
    slug = models.SlugField('Slug', max_length=140, unique=True)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=0)
    period = models.CharField('Период', max_length=40, default='/ мес')
    product_type = models.CharField('Тип товара', max_length=20, choices=ProductType.choices, default=ProductType.OTHER)
    duration_days = models.PositiveIntegerField('Срок действия, дней', default=30)
    icon = models.CharField('FontAwesome класс', max_length=120, default='fa-solid fa-gem')
    badge = models.CharField('Бейдж', max_length=50, blank=True)
    highlight = models.CharField('Выделение', max_length=20, choices=Highlight.choices, default=Highlight.DEFAULT)
    sort_order = models.PositiveIntegerField('Сортировка', default=100)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Товар магазина'
        verbose_name_plural = 'Товары магазина'
        ordering = ['sort_order', 'id']
        indexes = [models.Index(fields=['is_active', 'sort_order'], name='shop_active_sort_idx')]

    def __str__(self) -> str:
        return self.title


class Rule(TimeStampedModel):
    title = models.CharField('Заголовок', max_length=180)
    description = models.TextField('Описание')
    points = models.JSONField('Пункты правил', default=list, blank=True)
    sort_order = models.PositiveIntegerField('Сортировка', default=100)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Правило'
        verbose_name_plural = 'Правила'
        ordering = ['sort_order', 'id']
        indexes = [models.Index(fields=['is_active', 'sort_order'], name='rule_active_sort_idx')]

    def __str__(self) -> str:
        return self.title


class CaseReward(TimeStampedModel):
    class Rarity(models.TextChoices):
        GRAY = 'gray', 'Серый'
        BLUE = 'blue', 'Синий'
        CYAN = 'cyan', 'Голубой'
        PURPLE = 'purple', 'Фиолетовый'
        RED = 'red', 'Красный'
        GOLD = 'gold', 'Золотой'

    title = models.CharField('Название', max_length=120)
    rarity = models.CharField('Редкость', max_length=20, choices=Rarity.choices, default=Rarity.GRAY)
    icon = models.CharField('FontAwesome класс или custom-logo', max_length=120, default='fa-solid fa-coins')
    chance = models.DecimalField('Шанс, %', max_digits=5, decimal_places=2)
    credits_delta = models.PositiveIntegerField('Кредиты к начислению', default=0)
    grants_vip = models.BooleanField('Выдаёт VIP', default=False)
    grants_admin = models.BooleanField('Выдаёт админку', default=False)
    is_active = models.BooleanField('Активна', default=True)
    sort_order = models.PositiveIntegerField('Сортировка', default=100)

    class Meta:
        verbose_name = 'Награда колеса'
        verbose_name_plural = 'Награды колеса'
        ordering = ['sort_order', 'id']
        indexes = [models.Index(fields=['is_active', 'sort_order'], name='reward_active_sort_idx')]

    def __str__(self) -> str:
        return f'{self.title} ({self.chance}%)'


class CaseSpin(TimeStampedModel):
    user = models.ForeignKey(SteamUser, on_delete=models.CASCADE, related_name='case_spins', verbose_name='Пользователь')
    reward = models.ForeignKey(CaseReward, on_delete=models.PROTECT, related_name='spins', verbose_name='Награда')

    class Meta:
        verbose_name = 'Прокрутка бонусного колеса'
        verbose_name_plural = 'Прокрутки бонусного колеса'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'], name='spin_user_created_idx')]

    def __str__(self) -> str:
        return f'{self.user} → {self.reward}'


class PurchaseRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает обработки'
        APPROVED = 'approved', 'Одобрена'
        REJECTED = 'rejected', 'Отклонена'
        CANCELED = 'canceled', 'Отменена'

    user = models.ForeignKey(SteamUser, on_delete=models.CASCADE, related_name='purchase_requests', verbose_name='Пользователь')
    product = models.ForeignKey(ShopProduct, on_delete=models.PROTECT, related_name='purchase_requests', verbose_name='Товар')
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.PENDING)
    comment = models.TextField('Комментарий администратора', blank=True)

    class Meta:
        verbose_name = 'Заявка на покупку'
        verbose_name_plural = 'Заявки на покупки'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='purchase_user_created_idx'),
            models.Index(fields=['status', '-created_at'], name='purchase_status_created_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                condition=models.Q(status='pending'),
                name='unique_pending_purchase_per_product',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} → {self.product} [{self.status}]'
