import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.products.models import Category, Product
from apps.orders.models import Cart, CartItem

User = get_user_model()


class TestAuthenticationAPI:
    """Test authentication API endpoints."""
    
    def test_user_registration(self, client):
        """Test user registration."""
        url = reverse('users:register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'user' in response.data

    def test_user_login(self, client, user):
        """Test user login."""
        url = reverse('users:login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'user' in response.data

    def test_user_profile(self, authenticated_client, user):
        """Test user profile retrieval."""
        url = reverse('users:profile')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_change_password(self, authenticated_client, user):
        """Test password change."""
        url = reverse('users:change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

    def test_logout(self, authenticated_client, user):
        """Test user logout."""
        url = reverse('users:logout')
        # Get refresh token
        refresh = RefreshToken.for_user(user)
        data = {'refresh': str(refresh)}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK


class TestProductsAPI:
    """Test products API endpoints."""
    
    def test_category_list(self, client):
        """Test category list."""
        Category.objects.create(name='Test Category', description='Test description')
        url = reverse('products:category-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_product_list(self, client, product):
        """Test product list."""
        url = reverse('products:product-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_product_detail(self, client, product):
        """Test product detail."""
        url = reverse('products:product-detail', kwargs={'slug': product.slug})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name

    def test_product_search(self, client, product):
        """Test product search."""
        url = reverse('products:product-search')
        response = client.get(url, {'q': 'Test'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_featured_products(self, client, product):
        """Test featured products."""
        product.is_featured = True
        product.save()
        url = reverse('products:featured-products')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_product_filtering(self, client, category, product):
        """Test product filtering."""
        url = reverse('products:product-list')
        response = client.get(url, {'category': category.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_product_ordering(self, client, product):
        """Test product ordering."""
        url = reverse('products:product-list')
        response = client.get(url, {'ordering': 'price'})
        assert response.status_code == status.HTTP_200_OK


class TestOrdersAPI:
    """Test orders API endpoints."""
    
    def test_cart_retrieval(self, authenticated_client, user):
        """Test cart retrieval."""
        url = reverse('orders:cart')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0

    def test_add_to_cart(self, authenticated_client, product):
        """Test adding item to cart."""
        url = reverse('orders:add-to-cart')
        data = {
            'product_id': product.id,
            'quantity': 2
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_cart_item_list(self, authenticated_client, cart, product):
        """Test cart item list."""
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2,
            unit_price=product.price
        )
        url = reverse('orders:cart-item-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_update_cart_item_quantity(self, authenticated_client, cart, product):
        """Test updating cart item quantity."""
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2,
            unit_price=product.price
        )
        url = reverse('orders:update-cart-item-quantity', kwargs={'item_id': cart_item.id})
        data = {'quantity': 5}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['quantity'] == 5

    def test_remove_from_cart(self, authenticated_client, cart, product):
        """Test removing item from cart."""
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2,
            unit_price=product.price
        )
        url = reverse('orders:remove-from-cart', kwargs={'item_id': cart_item.id})
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK

    def test_clear_cart(self, authenticated_client, cart, product):
        """Test clearing cart."""
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2,
            unit_price=product.price
        )
        url = reverse('orders:clear-cart')
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK

    def test_order_creation(self, authenticated_client, product):
        """Test order creation."""
        # Add item to cart first
        cart_url = reverse('orders:add-to-cart')
        cart_data = {
            'product_id': product.id,
            'quantity': 2
        }
        authenticated_client.post(cart_url, cart_data, format='json')
        
        # Create order
        url = reverse('orders:checkout')
        data = {
            'billing_first_name': 'John',
            'billing_last_name': 'Doe',
            'billing_email': 'john@example.com',
            'billing_phone': '1234567890',
            'billing_address_line_1': '123 Main St',
            'billing_city': 'Test City',
            'billing_state': 'Test State',
            'billing_postal_code': '12345',
            'billing_country': 'Test Country',
            'shipping_first_name': 'John',
            'shipping_last_name': 'Doe',
            'shipping_phone': '1234567890',
            'shipping_address_line_1': '123 Main St',
            'shipping_city': 'Test City',
            'shipping_state': 'Test State',
            'shipping_postal_code': '12345',
            'shipping_country': 'Test Country'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'order_number' in response.data

    def test_order_list(self, authenticated_client, user):
        """Test order list."""
        from apps.orders.models import Order
        Order.objects.create(
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
        url = reverse('orders:order-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


class TestCoreAPI:
    """Test core API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        url = reverse('core:health-check')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'

    def test_api_info(self, client):
        """Test API info endpoint."""
        url = reverse('core:api-info')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'name' in response.data
        assert 'version' in response.data

    def test_server_time(self, client):
        """Test server time endpoint."""
        url = reverse('core:server-time')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'server_time' in response.data
        assert 'timezone' in response.data
