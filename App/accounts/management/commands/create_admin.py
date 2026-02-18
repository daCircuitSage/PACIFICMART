from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser from environment variables (for Render deployment)'

    def handle(self, *args, **options):
        # Read from environment variables
        admin_email = os.getenv('ADMIN_EMAIL', None)
        admin_password = os.getenv('ADMIN_PASSWORD', None)
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_first_name = os.getenv('ADMIN_FIRST_NAME', 'Admin')
        admin_last_name = os.getenv('ADMIN_LAST_NAME', 'User')

        # Validate
        if not admin_email or not admin_password:
            self.stdout.write(
                self.style.WARNING(
                    'Set ADMIN_EMAIL and ADMIN_PASSWORD environment variables to create admin user'
                )
            )
            return

        # Check if superuser already exists
        if User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.get(email=admin_email)
            if admin_user.is_superuser:
                self.stdout.write(
                    self.style.WARNING(f'Admin user with email {admin_email} already exists')
                )
                return
            else:
                # Upgrade existing user to superuser
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.is_admin = True
                admin_user.is_superadmin = True
                admin_user.is_active = True
                admin_user.set_password(admin_password)
                admin_user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Upgraded {admin_email} to superuser')
                )
                return

        # Create new superuser
        try:
            admin_user = User.objects.create_superuser(
                first_name=admin_first_name,
                last_name=admin_last_name,
                email=admin_email,
                username=admin_email.split('@')[0],
                password=admin_password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: {admin_email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )
