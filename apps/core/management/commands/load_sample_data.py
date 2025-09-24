import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.orders.models import Cart, CartItem, Order, OrderItem
from apps.products.models import (
    Category,
    Product,
    ProductImage,
    ProductReview,
    ProductVariant,
)
from apps.users.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Load sample data for testing"

    def handle(self, *args, **options):
        self.stdout.write("Loading sample data...")

        # Create categories
        categories_data = [
            {"name": "Electronics", "description": "Electronic devices and gadgets"},
            {"name": "Clothing", "description": "Fashion and apparel"},
            {"name": "Books", "description": "Books and educational materials"},
            {"name": "Home & Garden", "description": "Home improvement and gardening"},
            {"name": "Sports", "description": "Sports and fitness equipment"},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"], defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create products
        products_data = [
            {
                "name": "iPhone 15 Pro",
                "description": "Latest iPhone with advanced camera system",
                "short_description": "Premium smartphone with Pro camera",
                "sku": "IPH15PRO001",
                "price": Decimal("999.99"),
                "compare_price": Decimal("1099.99"),
                "stock_quantity": 50,
                "category": categories[0],
                "is_featured": True,
            },
            {
                "name": "Samsung Galaxy S24",
                "description": "Android flagship with AI features",
                "short_description": "AI-powered Android smartphone",
                "sku": "SGS24001",
                "price": Decimal("899.99"),
                "compare_price": Decimal("999.99"),
                "stock_quantity": 30,
                "category": categories[0],
                "is_featured": True,
            },
            {
                "name": "Nike Air Max 270",
                "description": "Comfortable running shoes with Air Max technology",
                "short_description": "Premium running shoes",
                "sku": "NAM270001",
                "price": Decimal("150.00"),
                "compare_price": Decimal("180.00"),
                "stock_quantity": 100,
                "category": categories[1],
            },
            {
                "name": "Python Programming Book",
                "description": "Complete guide to Python programming",
                "short_description": "Learn Python from basics to advanced",
                "sku": "PYTHON001",
                "price": Decimal("49.99"),
                "compare_price": Decimal("59.99"),
                "stock_quantity": 200,
                "category": categories[2],
            },
            {
                "name": "Garden Tool Set",
                "description": "Complete set of gardening tools",
                "short_description": "Professional gardening tools",
                "sku": "GTS001",
                "price": Decimal("79.99"),
                "compare_price": Decimal("99.99"),
                "stock_quantity": 25,
                "category": categories[3],
            },
            {
                "name": "Yoga Mat",
                "description": "Non-slip yoga mat for all exercises",
                "short_description": "Premium yoga mat",
                "sku": "YM001",
                "price": Decimal("29.99"),
                "compare_price": Decimal("39.99"),
                "stock_quantity": 75,
                "category": categories[4],
            },
        ]

        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=prod_data["sku"], defaults=prod_data
            )
            products.append(product)
            if created:
                self.stdout.write(f"Created product: {product.name}")

        # Create product variants
        for product in products[:3]:  # Only for first 3 products
            variants_data = [
                {"name": "Black", "sku": f"{product.sku}-BLK", "price": product.price},
                {"name": "White", "sku": f"{product.sku}-WHT", "price": product.price},
                {"name": "Blue", "sku": f"{product.sku}-BLU", "price": product.price},
            ]
            for var_data in variants_data:
                ProductVariant.objects.get_or_create(
                    product=product,
                    name=var_data["name"],
                    defaults={
                        "sku": var_data["sku"],
                        "price": var_data["price"],
                        "stock_quantity": random.randint(10, 50),
                    },
                )

        # Create product reviews
        users = User.objects.all()
        for product in products:
            for _ in range(random.randint(2, 5)):
                user = random.choice(users)
                ProductReview.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults={
                        "rating": random.randint(3, 5),
                        "title": f"Great {product.name}",
                        "comment": f"I really love this {product.name}. Highly recommended!",
                        # 75% approved
                        "is_approved": random.choice([True, True, True, False]),
                        "is_verified_purchase": random.choice([True, False]),
                    },
                )

        # Create orders
        for i in range(10):
            user = random.choice(users)
            order = Order.objects.create(
                user=user,
                status=random.choice(
                    ["pending", "confirmed", "processing", "shipped", "delivered"]
                ),
                payment_status=random.choice(["pending", "paid", "failed"]),
                subtotal=Decimal("0.00"),
                tax_amount=Decimal("0.00"),
                shipping_amount=Decimal("10.00"),
                discount_amount=Decimal("0.00"),
                total_amount=Decimal("0.00"),
                billing_first_name=user.first_name or "John",
                billing_last_name=user.last_name or "Doe",
                billing_email=user.email,
                billing_phone="+1234567890",
                billing_address_line_1="123 Main St",
                billing_city="New York",
                billing_state="NY",
                billing_postal_code="10001",
                billing_country="USA",
                shipping_first_name=user.first_name or "John",
                shipping_last_name=user.last_name or "Doe",
                shipping_phone="+1234567890",
                shipping_address_line_1="123 Main St",
                shipping_city="New York",
                shipping_state="NY",
                shipping_postal_code="10001",
                shipping_country="USA",
            )

            # Add order items
            selected_products = random.sample(products, random.randint(1, 3))
            subtotal = Decimal("0.00")

            for product in selected_products:
                quantity = random.randint(1, 3)
                unit_price = product.price
                total_price = unit_price * quantity
                subtotal += total_price

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                )

            # Update order totals
            order.subtotal = subtotal
            order.tax_amount = subtotal * Decimal("0.08")  # 8% tax
            order.total_amount = (
                order.subtotal
                + order.tax_amount
                + order.shipping_amount
                - order.discount_amount
            )
            order.save()

            self.stdout.write(f"Created order: {order.order_number}")

        # Create user profiles for existing users
        for user in users:
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "bio": f"This is {user.first_name or user.username}'s profile",
                    "location": random.choice(
                        ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
                    ),
                    "phone_number": "+1234567890",
                    "website": f"https://{user.username}.com",
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully loaded sample data:\n"
                f"- {User.objects.count()} users\n"
                f"- {Category.objects.count()} categories\n"
                f"- {Product.objects.count()} products\n"
                f"- {ProductVariant.objects.count()} product variants\n"
                f"- {ProductReview.objects.count()} product reviews\n"
                f"- {Order.objects.count()} orders\n"
                f"- {OrderItem.objects.count()} order items\n"
                f"- {UserProfile.objects.count()} user profiles"
            )
        )
