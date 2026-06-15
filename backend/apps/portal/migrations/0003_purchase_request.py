import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0002_performance_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Ожидает обработки'), ('approved', 'Одобрена'), ('rejected', 'Отклонена'), ('canceled', 'Отменена')], default='pending', max_length=20, verbose_name='Статус')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий администратора')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchase_requests', to='portal.shopproduct', verbose_name='Товар')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_requests', to='portal.steamuser', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заявка на покупку',
                'verbose_name_plural': 'Заявки на покупки',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='purchaserequest',
            index=models.Index(fields=['user', '-created_at'], name='purchase_user_created_idx'),
        ),
        migrations.AddIndex(
            model_name='purchaserequest',
            index=models.Index(fields=['status', '-created_at'], name='purchase_status_created_idx'),
        ),
    ]
