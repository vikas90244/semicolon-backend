from django.core.management.base import BaseCommand
from users.models import SemicolonUserModel


class Command(BaseCommand):
    help = 'Create or reset the demo user account'

    def handle(self, *args, **options):
        demo_email = "demo@semicolon.app"
        demo_username = "demo_user"
        demo_password = "demo123456"

        # Delete existing demo user if exists
        SemicolonUserModel.objects.filter(email=demo_email).delete()

        # Create fresh demo user
        user = SemicolonUserModel.objects.create_user(
            email=demo_email,
            username=demo_username,
            password=demo_password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f' Demo user created successfully!\n'
                f'  Email: {demo_email}\n'
                f'  Password: {demo_password}\n'
                f'  User ID: {user.userId}'
            )
        )
