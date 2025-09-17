from django.contrib import admin
from django.shortcuts import render
from django.db.models import Sum, F
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAdminSite(admin.AdminSite):
    """
    Custom admin site with enhanced dashboard.
    """
    site_header = "Django REST API Admin"
    site_title = "API Admin"
    index_title = "Welcome to Django REST API Administration"

    def index(self, request, extra_context=None):
        """
        Custom admin index with real statistics.
        """
        # Import models here to avoid circular imports
        from apps.products.models import Product, Category
        from apps.orders.models import Order, OrderItem

        # Get statistics
        user_count = User.objects.count()
        product_count = Product.objects.filter(is_active=True).count()
        category_count = Category.objects.filter(is_active=True).count()
        order_count = Order.objects.count()

        # Calculate revenue
        revenue = Order.objects.filter(
            payment_status='paid'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        # Recent orders
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]

        # Low stock products
        low_stock_products = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=F('low_stock_threshold')
        )[:5]

        # Recent users
        recent_users = User.objects.order_by('-date_joined')[:5]

        context = {
            'user_count': user_count,
            'product_count': product_count,
            'category_count': category_count,
            'order_count': order_count,
            'revenue': revenue,
            'recent_orders': recent_orders,
            'low_stock_products': low_stock_products,
            'recent_users': recent_users,
        }

        if extra_context:
            context.update(extra_context)

        return render(request, 'admin/index.html', context)


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')
