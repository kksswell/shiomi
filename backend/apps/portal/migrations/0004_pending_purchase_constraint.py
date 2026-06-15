from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('portal', '0003_purchase_request'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='purchaserequest',
            constraint=models.UniqueConstraint(
                fields=('user', 'product'),
                condition=models.Q(('status', 'pending')),
                name='unique_pending_purchase_per_product',
            ),
        ),
    ]
