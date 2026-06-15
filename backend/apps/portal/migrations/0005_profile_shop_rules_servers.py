from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def seed_servers_and_enhance_content(apps, schema_editor):
    GameServer = apps.get_model('portal', 'GameServer')
    ShopProduct = apps.get_model('portal', 'ShopProduct')
    Rule = apps.get_model('portal', 'Rule')

    GameServer.objects.update_or_create(
        slug='public',
        defaults={
            'title': 'PUBLIC',
            'mode': 'Соревновательный режим',
            'map_name': 'CS2 Community',
            'description': 'Премиальный PUBLIC-сервер SHIOMI: тёмный интерфейс, честная игра, бонусы и Steam-профиль.',
            'host': '170.168.115.48',
            'port': 27115,
            'max_players': 24,
            'mock_players': 0,
            'status_mode': 'auto',
            'connect_url': 'steam://connect/170.168.115.48:27115',
            'sort_order': 10,
            'is_active': True,
        },
    )

    product_types = {
        'shiomi-status': ('status', 30),
        'vip-status': ('vip', 30),
        'premium-vip': ('premium', 30),
        'admin': ('admin', 30),
    }
    for slug, (product_type, days) in product_types.items():
        ShopProduct.objects.filter(slug=slug).update(product_type=product_type, duration_days=days)

    rule_points = {
        '1. Игровой процесс': [
            'Запрещены читы, макросы, скрипты и любые программы, дающие преимущество.',
            'Запрещено намеренно мешать команде, сливать позиции и портить игру.',
            'Наказание выбирается администрацией: предупреждение, кик, бан или перманентный бан.',
        ],
        '2. Общение в чате и микрофоне': [
            'Запрещены оскорбления, токсичность, провокации и дискриминация.',
            'Запрещён флуд, спам, реклама и навязчивые звуки в микрофон.',
            'Уважайте игроков и администрацию, даже если матч идёт тяжело.',
        ],
        '3. Обязанности Администрации': [
            'Администратор обязан действовать спокойно, честно и по правилам проекта.',
            'Запрещено злоупотреблять правами, выдавать наказания без причины и мешать игрокам.',
            'Спорные ситуации фиксируются и разбираются руководством проекта.',
        ],
    }
    for title, points in rule_points.items():
        Rule.objects.filter(title=title).update(points=points)


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0004_pending_purchase_constraint'),
    ]

    operations = [
        migrations.AddField(
            model_name='steamuser',
            name='admin_expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Админка до'),
        ),
        migrations.AddField(
            model_name='steamuser',
            name='first_login_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Первый вход'),
        ),
        migrations.AddField(
            model_name='steamuser',
            name='last_login_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Последний вход'),
        ),
        migrations.AddField(
            model_name='steamuser',
            name='vip_expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='VIP до'),
        ),
        migrations.AddField(
            model_name='shopproduct',
            name='duration_days',
            field=models.PositiveIntegerField(default=30, verbose_name='Срок действия, дней'),
        ),
        migrations.AddField(
            model_name='shopproduct',
            name='product_type',
            field=models.CharField(choices=[('vip', 'VIP'), ('premium', 'Premium VIP'), ('admin', 'Админка'), ('status', 'SHIOMI Status'), ('credits', 'Кредиты'), ('other', 'Другое')], default='other', max_length=20, verbose_name='Тип товара'),
        ),
        migrations.AddField(
            model_name='rule',
            name='points',
            field=models.JSONField(blank=True, default=list, verbose_name='Пункты правил'),
        ),
        migrations.CreateModel(
            name='GameServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(default='PUBLIC', max_length=120, verbose_name='Название')),
                ('slug', models.SlugField(default='public', max_length=140, unique=True, verbose_name='Slug')),
                ('mode', models.CharField(default='Соревновательный режим', max_length=120, verbose_name='Режим')),
                ('map_name', models.CharField(blank=True, default='CS2 Community', max_length=120, verbose_name='Карта/описание')),
                ('description', models.TextField(blank=True, default='Тёмный CS2-сервер SHIOMI с премиальной атмосферой.', verbose_name='Описание')),
                ('host', models.CharField(default='170.168.115.48', max_length=120, verbose_name='Host/IP')),
                ('port', models.PositiveIntegerField(default=27115, verbose_name='Port')),
                ('max_players', models.PositiveIntegerField(default=24, verbose_name='Максимум игроков')),
                ('mock_players', models.PositiveIntegerField(default=0, verbose_name='Моковый онлайн')),
                ('status_mode', models.CharField(choices=[('auto', 'Авто через Source Query'), ('mock', 'Моковые данные'), ('disabled', 'Отключён')], default='auto', max_length=20, verbose_name='Источник статуса')),
                ('image', models.ImageField(blank=True, upload_to='servers/', verbose_name='Фон карточки')),
                ('connect_url', models.CharField(blank=True, max_length=255, verbose_name='Ссылка подключения')),
                ('sort_order', models.PositiveIntegerField(default=100, verbose_name='Сортировка')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
            ],
            options={
                'verbose_name': 'Игровой сервер',
                'verbose_name_plural': 'Игровые серверы',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='gameserver',
            index=models.Index(fields=['is_active', 'sort_order'], name='server_active_sort_idx'),
        ),
        migrations.AddIndex(
            model_name='steamuser',
            index=models.Index(fields=['steam_id64'], name='steam_user_id64_idx'),
        ),
        migrations.RunPython(seed_servers_and_enhance_content, migrations.RunPython.noop),
    ]
