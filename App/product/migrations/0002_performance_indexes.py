# Generated for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['product_slug'], name='product_product_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_available'], name='product_is_available_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['created_at'], name='product_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['product_category'], name='product_category_idx'),
        ),
        migrations.AddIndex(
            model_name='variation',
            index=models.Index(fields=['product'], name='variation_product_idx'),
        ),
        migrations.AddIndex(
            model_name='reviewrating',
            index=models.Index(fields=['product'], name='review_product_idx'),
        ),
        migrations.AddIndex(
            model_name='reviewrating',
            index=models.Index(fields=['user'], name='review_user_idx'),
        ),
        migrations.AddIndex(
            model_name='reviewrating',
            index=models.Index(fields=['status'], name='review_status_idx'),
        ),
    ]
