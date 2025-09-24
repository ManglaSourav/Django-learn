import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.orders.models import Cart, CartItem, Order, OrderItem
from apps.products.models import (
    Category,
    Product,
    ProductImage,
    ProductReview,
    ProductVariant,
)
from apps.users.models import User, UserProfile


class TestUserModel:
    """Test User model."""

    def test_user_creation(self):
        """Test user creation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_user_full_name(self):
        """Test user full name property."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        assert user.full_name == 'John Doe'

    def test_user_short_name(self):
        """Test user short name property."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John'
        )
        assert user.get_short_name() == 'John'

    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'test@example.com'


class TestUserProfileModel:
    """Test UserProfile model."""

    def test_profile_creation(self, user):
        """Test profile creation."""
        profile = UserProfile.objects.create(
            user=user,
            bio='Test bio',
            location='Test City'
        )
        assert profile.user == user
        assert profile.bio == 'Test bio'
        assert profile.location == 'Test City'

    def test_profile_str(self, user):
        """Test profile string representation."""
        profile = UserProfile.objects.create(user=user)
        assert str(profile) == f"{user.email}'s Profile"


class TestCategoryModel:
    """Test Category model."""

    def test_category_creation(self):
        """Test category creation."""
        category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )
        assert category.name == 'Test Category'
        assert category.slug == 'test-category'
        assert category.is_active
        assert not category.is_deleted

    def test_category_slug_generation(self):
        """Test category slug generation."""
        category = Category.objects.create(name='Test Category Name')
        assert category.slug == 'test-category-name'

    def test_category_str(self):
        """Test category string representation."""
        category = Category.objects.create(name='Test Category')
        assert str(category) == 'Test Category'

    def test_category_soft_delete(self):
        """Test category soft delete."""
        category = Category.objects.create(name='Test Category')
        category.delete()
        assert category.is_deleted
        assert category.deleted_at is not None


class TestProductModel:
    """Test Product model."""

    def test_product_creation(self, category):
        """Test product creation."""
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            short_description='Short description',
            sku='TEST-001',
            price=99.99,
            category=category
        )
        assert product.name == 'Test Product'
        assert product.slug == 'test-product'
        assert product.price == 99.99
        assert product.category == category
        assert product.is_active
        assert not product.is_deleted

    def test_product_slug_generation(self, category):
        """Test product slug generation."""
        product = Product.objects.create(
            name='Test Product Name',
            sku='TEST-001',
            price=99.99,
            category=category
        )
        assert product.slug == 'test-product-name'

    def test_product_str(self, category):
        """Test product string representation."""
        product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            price=99.99,
            category=category
        )
        assert str(product) == 'Test Product'

    def test_product_is_low_stock(self, category):
        """Test product low stock property."""
        product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            price=99.99,
            category=category,
            stock_quantity=3,
            low_stock_threshold=5
        )
        assert product.is_low_stock

    def test_product_discount_percentage(self, category):
        """Test product discount percentage property."""
        product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            price=80.00,
            compare_price=100.00,
            category=category
        )
        assert product.discount_percentage == 20.0


class TestOrderModel:
    """Test Order model."""

    def test_order_creation(self, user):
        """Test order creation."""
        order = Order.objects.create(
            user=user,
            subtotal=100.00,
            tax_amount=10.00,
            shipping_amount=5.00,
            total_amount=115.00,
            billing_first_name='John',
            billing_last_name='Doe',
            billing_email='john@example.com',
            billing_phone='1234567890',
            billing_address_line_1='123 Main St',
            billing_city='Test City',
            billing_state='Test State',
            billing_postal_code='12345',
            billing_country='Test Country',
            shipping_first_name='John',
            shipping_last_name='Doe',
            shipping_phone='1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='Test City',
            shipping_state='Test State',
            shipping_postal_code='12345',
            shipping_country='Test Country'
        )
        assert order.user == user
        assert order.order_number.startswith('ORD-')
        assert order.status == 'pending'
        assert order.payment_status == 'pending'

    def test_order_str(self, user):
        """Test order string representation."""
        order = Order.objects.create(
            user=user,
            subtotal=100.00,
            total_amount=115.00,
            billing_first_name='John',
            billing_last_name='Doe',
            billing_email='john@example.com',
            billing_phone='1234567890',
            billing_address_line_1='123 Main St',
            billing_city='Test City',
            billing_state='Test State',
            billing_postal_code='12345',
            billing_country='Test Country',
            shipping_first_name='John',
            shipping_last_name='Doe',
            shipping_phone='1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='Test City',
            shipping_state='Test State',
            shipping_postal_code='12345',
            shipping_country='Test Country'
        )
        assert str(order) == f"Order {order.order_number}"

    def test_order_can_be_cancelled(self, user):
        """Test order cancellation check."""
        order = Order.objects.create(
            user=user,
            subtotal=100.00,
            total_amount=115.00,
            status='pending',
            billing_first_name='John',
            billing_last_name='Doe',
            billing_email='john@example.com',
            billing_phone='1234567890',
            billing_address_line_1='123 Main St',
            billing_city='Test City',
            billing_state='Test State',
            billing_postal_code='12345',
            billing_country='Test Country',
            shipping_first_name='John',
            shipping_last_name='Doe',
            shipping_phone='1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='Test City',
            shipping_state='Test State',
            shipping_postal_code='12345',
            shipping_country='Test Country'
        )
        assert order.can_be_cancelled()


class TestCartModel:
    """Test Cart model."""

    def test_cart_creation(self, user):
        """Test cart creation."""
        cart = Cart.objects.create(user=user)
        assert cart.user == user
        assert cart.total_items == 0
        assert cart.total_amount == 0

    def test_cart_str(self, user):
        """Test cart string representation."""
        cart = Cart.objects.create(user=user)
        assert str(cart) == f"Cart for {user.email}"
