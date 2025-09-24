from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser with custom fields"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, help="Username")
        parser.add_argument("--email", type=str, help="Email")
        parser.add_argument("--password", type=str, help="Password")
        parser.add_argument("--first-name", type=str, help="First name")
        parser.add_argument("--last-name", type=str, help="Last name")

    def handle(self, *args, **options):
        username = options.get("username") or "admin"
        email = options.get("email") or "admin@example.com"
        password = options.get("password") or "admin123"
        first_name = options.get("first_name") or "Admin"
        last_name = options.get("last_name") or "User"

        with transaction.atomic():
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f"User with email {email} already exists")
                )
                return

            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully created superuser: {user.email}")
            )
