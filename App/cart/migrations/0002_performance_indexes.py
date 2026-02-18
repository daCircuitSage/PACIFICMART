# Generated for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='cart',
            index=models.Index(fields=['cart_id'], name='cart_cart_id_idx'),
        ),
        migrations.AddIndex(
            model_name='cartitems',
            index=models.Index(fields=['user'], name='cartitems_user_idx'),
        ),
        migrations.AddIndex(
            model_name='cartitems',
            index=models.Index(fields=['product'], name='cartitems_product_idx'),
        ),
        migrations.AddIndex(
            model_name='cartitems',
            index=models.Index(fields=['cart'], name='cartitems_cart_idx'),
        ),
        migrations.AddIndex(
            model_name='cartitems',
            index=models.Index(fields=['is_active'], name='cartitems_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='checkoutdb',
            index=models.Index(fields=['user'], name='checkoutdb_user_idx'),
        ),
    ]
