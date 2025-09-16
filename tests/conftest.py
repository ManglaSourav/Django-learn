import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
from apps.orders.models import Cart

User = get_user_model()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def category():
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        description='Test category description'
    )


@pytest.fixture
def product(category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        description='Test product description',
        short_description='Short description',
        sku='TEST-001',
        price=99.99,
        category=category,
        stock_quantity=100
    )


@pytest.fixture
def cart(user):
    """Create a test cart."""
    return Cart.objects.create(user=user)


@pytest.fixture
def authenticated_client(client, user):
    """Authenticated test client."""
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Admin test client."""
    client.force_login(admin_user)
    return client
