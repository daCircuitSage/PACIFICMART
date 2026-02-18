# Generated for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_number'], name='order_order_number_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['user'], name='order_user_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['is_ordered'], name='order_is_ordered_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['created_at'], name='order_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='orderproduct',
            index=models.Index(fields=['order'], name='orderproduct_order_idx'),
        ),
        migrations.AddIndex(
            model_name='orderproduct',
            index=models.Index(fields=['product'], name='orderproduct_product_idx'),
        ),
        migrations.AddIndex(
            model_name='orderproduct',
            index=models.Index(fields=['user'], name='orderproduct_user_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['user'], name='payment_user_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['payment_id'], name='payment_payment_id_idx'),
        ),
    ]
