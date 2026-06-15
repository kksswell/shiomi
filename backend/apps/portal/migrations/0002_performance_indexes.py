from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='steamuser',
            index=models.Index(fields=['-created_at'], name='steam_user_created_idx'),
        ),
        migrations.AddIndex(
            model_name='shopproduct',
            index=models.Index(fields=['is_active', 'sort_order'], name='shop_active_sort_idx'),
        ),
        migrations.AddIndex(
            model_name='rule',
            index=models.Index(fields=['is_active', 'sort_order'], name='rule_active_sort_idx'),
        ),
        migrations.AddIndex(
            model_name='casereward',
            index=models.Index(fields=['is_active', 'sort_order'], name='reward_active_sort_idx'),
        ),
        migrations.AddIndex(
            model_name='casespin',
            index=models.Index(fields=['user', '-created_at'], name='spin_user_created_idx'),
        ),
    ]
