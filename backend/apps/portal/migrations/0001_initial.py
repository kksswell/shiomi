from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


def seed_defaults(apps, _schema_editor):
    ShopProduct = apps.get_model('portal', 'ShopProduct')
    Rule = apps.get_model('portal', 'Rule')
    CaseReward = apps.get_model('portal', 'CaseReward')

    products = [
        {
            'title': 'SHIOMI STATUS',
            'slug': 'shiomi-status',
            'description': 'Полный доступ ко всем функциям: уникальный префикс [SHIOMI], иммунитет, доступ ко всем приватным скинам и ножам, х3 кредиты и кастомный цвет чата.',
            'price': Decimal('599'),
            'period': '/ мес',
            'icon': 'fa-solid fa-gem',
            'badge': 'EXCLUSIVE',
            'highlight': 'shiomi',
            'sort_order': 10,
        },
        {
            'title': 'VIP СТАТУС',
            'slug': 'vip-status',
            'description': 'Доступ к уникальным скинам, префиксам и тегам в табе, х2 кредиты.',
            'price': Decimal('249'),
            'period': '/ мес',
            'icon': 'fa-solid fa-crown text-blue',
            'badge': '',
            'highlight': 'default',
            'sort_order': 20,
        },
        {
            'title': 'PREMIUM VIP',
            'slug': 'premium-vip',
            'description': 'Все права обычного VIP + иммунитет к кику, кастомные трейлы и аура.',
            'price': Decimal('350'),
            'period': '/ мес',
            'icon': 'fa-solid fa-shield-halved',
            'badge': 'POPULAR',
            'highlight': 'premium',
            'sort_order': 30,
        },
        {
            'title': 'АДМИНКА',
            'slug': 'admin',
            'description': 'Возможность модерировать сервер, банить читеров и следить за порядком.',
            'price': Decimal('650'),
            'period': '/ мес',
            'icon': 'fa-solid fa-wand-magic-sparkles text-blue',
            'badge': '',
            'highlight': 'default',
            'sort_order': 40,
        },
    ]
    for item in products:
        ShopProduct.objects.update_or_create(slug=item['slug'], defaults=item)

    rules = [
        ('1. Игровой процесс', 'Запрещено использование любых сторонних программ, скриптов, макросов или читов, дающих преимущество над другими игроками. Наказание: перманентный бан.', 10),
        ('2. Общение в чате и микрофоне', 'Запрещены оскорбления игроков, администрации, разжигание конфликтов, спам, флуд и реклама сторонних ресурсов. Уважайте окружающих. Наказание: мут от 30 минут до суток.', 20),
        ('3. Обязанности Администрации', 'Администратор обязан следить за порядком и справедливо наказывать нарушителей. Администратору запрещено злоупотреблять правами или кикать игроков без весомой причины.', 30),
    ]
    for title, description, sort_order in rules:
        Rule.objects.update_or_create(title=title, defaults={'description': description, 'sort_order': sort_order, 'is_active': True})

    rewards = [
        ('100 Кредитов', 'gray', 'fa-solid fa-coins', Decimal('40.00'), 100, False, False, 10),
        ('500 Кредитов', 'blue', 'fa-solid fa-coins', Decimal('30.00'), 500, False, False, 20),
        ('VIP (3 дня)', 'cyan', 'fa-solid fa-crown', Decimal('18.00'), 0, True, False, 30),
        ('PREMIUM (3 дня)', 'purple', 'fa-solid fa-shield-halved', Decimal('8.00'), 0, True, False, 40),
        ('АДМИНКА (3 дня)', 'red', 'fa-solid fa-wand-magic-sparkles', Decimal('3.50'), 0, False, True, 50),
        ('SHIOMI STATUS', 'gold', 'custom-logo', Decimal('0.50'), 1500, True, False, 60),
    ]
    for title, rarity, icon, chance, credits_delta, grants_vip, grants_admin, sort_order in rewards:
        CaseReward.objects.update_or_create(
            title=title,
            defaults={
                'rarity': rarity,
                'icon': icon,
                'chance': chance,
                'credits_delta': credits_delta,
                'grants_vip': grants_vip,
                'grants_admin': grants_admin,
                'sort_order': sort_order,
                'is_active': True,
            },
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CaseReward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=120, verbose_name='Название')),
                ('rarity', models.CharField(choices=[('gray', 'Серый'), ('blue', 'Синий'), ('cyan', 'Голубой'), ('purple', 'Фиолетовый'), ('red', 'Красный'), ('gold', 'Золотой')], default='gray', max_length=20, verbose_name='Редкость')),
                ('icon', models.CharField(default='fa-solid fa-coins', max_length=120, verbose_name='FontAwesome класс или custom-logo')),
                ('chance', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Шанс, %')),
                ('credits_delta', models.PositiveIntegerField(default=0, verbose_name='Кредиты к начислению')),
                ('grants_vip', models.BooleanField(default=False, verbose_name='Выдаёт VIP')),
                ('grants_admin', models.BooleanField(default=False, verbose_name='Выдаёт админку')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('sort_order', models.PositiveIntegerField(default=100, verbose_name='Сортировка')),
            ],
            options={'verbose_name': 'Награда кейса', 'verbose_name_plural': 'Награды кейса', 'ordering': ['sort_order', 'id']},
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=180, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('sort_order', models.PositiveIntegerField(default=100, verbose_name='Сортировка')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
            ],
            options={'verbose_name': 'Правило', 'verbose_name_plural': 'Правила', 'ordering': ['sort_order', 'id']},
        ),
        migrations.CreateModel(
            name='ShopProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=120, verbose_name='Название')),
                ('slug', models.SlugField(max_length=140, unique=True, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.DecimalField(decimal_places=0, max_digits=10, verbose_name='Цена')),
                ('period', models.CharField(default='/ мес', max_length=40, verbose_name='Период')),
                ('icon', models.CharField(default='fa-solid fa-gem', max_length=120, verbose_name='FontAwesome класс')),
                ('badge', models.CharField(blank=True, max_length=50, verbose_name='Бейдж')),
                ('highlight', models.CharField(choices=[('default', 'Обычный'), ('premium', 'Premium'), ('shiomi', 'ShioMI')], default='default', max_length=20, verbose_name='Выделение')),
                ('sort_order', models.PositiveIntegerField(default=100, verbose_name='Сортировка')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
            ],
            options={'verbose_name': 'Товар магазина', 'verbose_name_plural': 'Товары магазина', 'ordering': ['sort_order', 'id']},
        ),
        migrations.CreateModel(
            name='SteamUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('steam_id64', models.CharField(max_length=32, unique=True, verbose_name='SteamID64')),
                ('steam_id2', models.CharField(blank=True, max_length=32, verbose_name='SteamID2')),
                ('username', models.CharField(max_length=255, verbose_name='Никнейм')),
                ('avatar_url', models.URLField(blank=True, verbose_name='Аватар')),
                ('is_vip', models.BooleanField(default=False, verbose_name='VIP')),
                ('is_server_admin', models.BooleanField(default=False, verbose_name='Админ сервера')),
                ('credits', models.PositiveIntegerField(default=0, verbose_name='Кредиты')),
                ('kills', models.PositiveIntegerField(default=0, verbose_name='Убийства')),
                ('deaths', models.PositiveIntegerField(default=0, verbose_name='Смерти')),
                ('headshots', models.PositiveIntegerField(default=0, verbose_name='Headshots')),
                ('level', models.PositiveIntegerField(default=1, verbose_name='Уровень')),
                ('last_spin_at', models.DateTimeField(blank=True, null=True, verbose_name='Последнее открытие кейса')),
            ],
            options={'verbose_name': 'Steam пользователь', 'verbose_name_plural': 'Steam пользователи', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='CaseSpin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reward', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='spins', to='portal.casereward', verbose_name='Награда')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='case_spins', to='portal.steamuser', verbose_name='Пользователь')),
            ],
            options={'verbose_name': 'Открытие кейса', 'verbose_name_plural': 'Открытия кейсов', 'ordering': ['-created_at']},
        ),
        migrations.RunPython(seed_defaults, migrations.RunPython.noop),
    ]
