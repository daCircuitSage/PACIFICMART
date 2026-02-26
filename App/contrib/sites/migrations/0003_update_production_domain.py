# Generated migration to update production domain

from django.db import migrations

def update_site_domain(apps, schema_editor):
    """Update the default site domain to production"""
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(id=1).update(
        domain='thepacificmart.onrender.com',
        name='PacificMart'
    )

def reverse_site_domain(apps, schema_editor):
    """Revert to development domain"""
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(id=1).update(
        domain='127.0.0.1:8001',
        name='PacificMart'
    )

class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(update_site_domain, reverse_site_domain),
    ]
