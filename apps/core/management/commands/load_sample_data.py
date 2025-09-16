from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product, ProductImage
from apps.orders.models import Cart
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Load sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample users
        users = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                email=f'user{i+1}@example.com',
                defaults={
                    'username': f'user{i+1}',
                    'first_name': f'User{i+1}',
                    'last_name': 'Test',
                    'is_verified': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)

        # Create sample categories
        categories = []
        category_names = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports']
        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Description for {name}',
                    'is_active': True
                }
            )
            categories.append(category)

        # Create sample products
        products = []
        product_names = [
            'Smartphone', 'Laptop', 'T-Shirt', 'Jeans', 'Python Book',
            'Garden Tools', 'Running Shoes', 'Headphones', 'Coffee Maker', 'Fitness Tracker'
        ]
        
        for i, name in enumerate(product_names):
            category = random.choice(categories)
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Detailed description for {name}',
                    'short_description': f'Short description for {name}',
                    'sku': f'PROD-{i+1:03d}',
                    'price': round(random.uniform(10, 1000), 2),
                    'stock_quantity': random.randint(0, 100),
                    'category': category,
                    'is_active': True,
                    'is_featured': random.choice([True, False])
                }
            )
            products.append(product)

        # Create carts for users
        for user in users:
            cart, created = Cart.objects.get_or_create(user=user)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {len(users)} users\n'
                f'- {len(categories)} categories\n'
                f'- {len(products)} products\n'
                f'- {len(users)} carts'
            )
        )
