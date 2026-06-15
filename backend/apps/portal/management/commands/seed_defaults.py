from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.portal.models import CaseReward, GameServer, Rule, ShopProduct


class Command(BaseCommand):
    help = 'Create or refresh safe default SHIOMI content for local/dev environments.'

    def handle(self, *args, **options):
        self.seed_server()
        self.seed_shop()
        self.seed_rules()
        self.seed_rewards()
        self.stdout.write(self.style.SUCCESS('Default SHIOMI content is ready.'))

    def seed_server(self):
        GameServer.objects.update_or_create(
            slug='public',
            defaults={
                'title': 'PUBLIC',
                'mode': 'Соревновательный режим',
                'map_name': 'CS2 Community',
                'description': 'Премиальный PUBLIC-сервер SHIOMI: быстрые раунды, чистая игра, бонусы и Steam-профиль.',
                'host': '170.168.115.48',
                'port': 27115,
                'max_players': 24,
                'mock_players': 0,
                'status_mode': GameServer.StatusMode.AUTO,
                'connect_url': 'steam://connect/170.168.115.48:27115',
                'sort_order': 10,
                'is_active': True,
            },
        )

    def seed_shop(self):
        items = [
            {
                'slug': 'shiomi-status',
                'title': 'SHIOMI STATUS',
                'description': 'Полный доступ ко всем функциям: уникальный префикс [SHIOMI], иммунитет, приватные скины и ножи, x3 кредиты и кастомный цвет чата.',
                'price': Decimal('599'),
                'period': '/ мес',
                'product_type': ShopProduct.ProductType.STATUS,
                'duration_days': 30,
                'icon': 'fa-solid fa-gem',
                'badge': 'EXCLUSIVE',
                'highlight': ShopProduct.Highlight.SHIOMI,
                'sort_order': 10,
            },
            {
                'slug': 'vip-status',
                'title': 'VIP СТАТУС',
                'description': 'Уникальные скины, префиксы, теги в TAB и x2 кредиты за активность на сервере.',
                'price': Decimal('249'),
                'period': '/ мес',
                'product_type': ShopProduct.ProductType.VIP,
                'duration_days': 30,
                'icon': 'fa-solid fa-crown text-blue',
                'badge': '',
                'highlight': ShopProduct.Highlight.DEFAULT,
                'sort_order': 20,
            },
            {
                'slug': 'premium-vip',
                'title': 'PREMIUM VIP',
                'description': 'Все права обычного VIP, иммунитет к кику, кастомные трейлы, аура и расширенные игровые бонусы.',
                'price': Decimal('350'),
                'period': '/ мес',
                'product_type': ShopProduct.ProductType.PREMIUM,
                'duration_days': 30,
                'icon': 'fa-solid fa-shield-halved',
                'badge': 'POPULAR',
                'highlight': ShopProduct.Highlight.PREMIUM,
                'sort_order': 30,
            },
            {
                'slug': 'admin',
                'title': 'АДМИНКА',
                'description': 'Возможность модерировать сервер, банить нарушителей, следить за порядком и помогать комьюнити.',
                'price': Decimal('650'),
                'period': '/ мес',
                'product_type': ShopProduct.ProductType.ADMIN,
                'duration_days': 30,
                'icon': 'fa-solid fa-wand-magic-sparkles text-blue',
                'badge': '',
                'highlight': ShopProduct.Highlight.DEFAULT,
                'sort_order': 40,
            },
        ]
        for item in items:
            ShopProduct.objects.update_or_create(slug=item.pop('slug'), defaults={**item, 'is_active': True})

    def seed_rules(self):
        items = [
            {
                'title': '1. Игровой процесс',
                'description': 'Правила честной игры на сервере SHIOMI.',
                'points': [
                    'Запрещены читы, макросы, скрипты и любые программы, дающие преимущество.',
                    'Запрещено намеренно мешать команде, сливать позиции и портить игру.',
                    'Запрещены обходы банов, баги карты и эксплуатация ошибок сервера.',
                ],
                'sort_order': 10,
            },
            {
                'title': '2. Общение в чате и микрофоне',
                'description': 'Комьюнити должно оставаться комфортным для всех игроков.',
                'points': [
                    'Запрещены оскорбления, токсичность, провокации и дискриминация.',
                    'Запрещён флуд, спам, реклама и навязчивые звуки в микрофон.',
                    'Уважайте игроков и администрацию, даже если матч идёт тяжело.',
                ],
                'sort_order': 20,
            },
            {
                'title': '3. Обязанности Администрации',
                'description': 'Администрация обязана действовать прозрачно и по правилам проекта.',
                'points': [
                    'Администратор обязан действовать спокойно, честно и по правилам проекта.',
                    'Запрещено злоупотреблять правами, выдавать наказания без причины и мешать игрокам.',
                    'Спорные ситуации фиксируются и разбираются руководством проекта.',
                ],
                'sort_order': 30,
            },
        ]
        for item in items:
            Rule.objects.update_or_create(title=item['title'], defaults={**item, 'is_active': True})

    def seed_rewards(self):
        items = [
            ('100 Кредитов', CaseReward.Rarity.GRAY, 'fa-solid fa-coins', Decimal('40.00'), 100, False, False, 10),
            ('500 Кредитов', CaseReward.Rarity.BLUE, 'fa-solid fa-coins', Decimal('30.00'), 500, False, False, 20),
            ('VIP (3 дня)', CaseReward.Rarity.CYAN, 'fa-solid fa-crown', Decimal('18.00'), 0, True, False, 30),
            ('PREMIUM (3 дня)', CaseReward.Rarity.PURPLE, 'fa-solid fa-shield-halved', Decimal('8.00'), 0, True, False, 40),
            ('АДМИНКА (3 дня)', CaseReward.Rarity.RED, 'fa-solid fa-wand-magic-sparkles', Decimal('3.50'), 0, False, True, 50),
            ('SHIOMI STATUS', CaseReward.Rarity.GOLD, 'custom-logo', Decimal('0.50'), 1000, True, True, 60),
        ]
        for title, rarity, icon, chance, credits, vip, admin, order in items:
            CaseReward.objects.update_or_create(
                title=title,
                defaults={
                    'rarity': rarity,
                    'icon': icon,
                    'chance': chance,
                    'credits_delta': credits,
                    'grants_vip': vip,
                    'grants_admin': admin,
                    'sort_order': order,
                    'is_active': True,
                },
            )
