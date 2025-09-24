import pytest
from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model

from apps.orders.serializers import CartSerializer, OrderSerializer
from apps.products.serializers import CategorySerializer, ProductListSerializer
from apps.users.serializers import (
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class TestUserRegistrationSerializer:
    """Test UserRegistrationSerializer."""

    def test_valid_registration_data(self):
        """Test valid registration data."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()

    def test_password_mismatch(self):
        """Test password mismatch validation."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "differentpass",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_weak_password(self):
        """Test weak password validation."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",
            "password_confirm": "123",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_create_user(self):
        """Test user creation."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")


class TestUserLoginSerializer:
    """Test UserLoginSerializer."""

    def test_valid_login_data(self, user):
        """Test valid login data."""
        data = {"email": "test@example.com", "password": "testpass123"}
        serializer = UserLoginSerializer(data=data)
        assert serializer.is_valid()

    def test_invalid_credentials(self):
        """Test invalid credentials."""
        data = {"email": "test@example.com", "password": "wrongpassword"}
        serializer = UserLoginSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_missing_fields(self):
        """Test missing required fields."""
        data = {"email": "test@example.com"}
        serializer = UserLoginSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors


class TestUserSerializer:
    """Test UserSerializer."""

    def test_user_serialization(self, user):
        """Test user serialization."""
        serializer = UserSerializer(user)
        data = serializer.data
        assert data["email"] == user.email
        assert data["username"] == user.username
        assert "full_name" in data
        assert "created_at" in data
        assert "updated_at" in data


class TestCategorySerializer:
    """Test CategorySerializer."""

    def test_category_serialization(self, category):
        """Test category serialization."""
        serializer = CategorySerializer(category)
        data = serializer.data
        assert data["name"] == category.name
        assert data["slug"] == category.slug
        assert data["is_active"] == category.is_active
        assert "product_count" in data
        assert "created_at" in data
        assert "updated_at" in data


class TestProductListSerializer:
    """Test ProductListSerializer."""

    def test_product_serialization(self, product):
        """Test product serialization."""
        serializer = ProductListSerializer(product)
        data = serializer.data
        assert data["name"] == product.name
        assert data["slug"] == product.slug
        assert data["price"] == str(product.price)
        assert data["category"] == product.category.id
        assert "average_rating" in data
        assert "review_count" in data
        assert "discount_percentage" in data
        assert "is_low_stock" in data


class TestOrderSerializer:
    """Test OrderSerializer."""

    def test_order_serialization(self, user):
        """Test order serialization."""
        order = Order.objects.create(
            user=user,
            subtotal=100.00,
            tax_amount=10.00,
            shipping_amount=5.00,
            total_amount=115.00,
            billing_first_name="John",
            billing_last_name="Doe",
            billing_email="john@example.com",
            billing_phone="1234567890",
            billing_address_line_1="123 Main St",
            billing_city="Test City",
            billing_state="Test State",
            billing_postal_code="12345",
            billing_country="Test Country",
            shipping_first_name="John",
            shipping_last_name="Doe",
            shipping_phone="1234567890",
            shipping_address_line_1="123 Main St",
            shipping_city="Test City",
            shipping_state="Test State",
            shipping_postal_code="12345",
            shipping_country="Test Country",
        )
        serializer = OrderSerializer(order)
        data = serializer.data
        assert data["order_number"] == order.order_number
        assert data["status"] == order.status
        assert data["total_amount"] == str(order.total_amount)
        assert "billing_full_name" in data
        assert "shipping_full_name" in data
        assert "can_be_cancelled" in data
        assert "can_be_refunded" in data


class TestCartSerializer:
    """Test CartSerializer."""

    def test_cart_serialization(self, cart):
        """Test cart serialization."""
        serializer = CartSerializer(cart)
        data = serializer.data
        assert data["total_items"] == cart.total_items
        assert data["total_amount"] == cart.total_amount
        assert "items" in data
        assert "created_at" in data
        assert "updated_at" in data
