from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.shortcuts import render

from apps.orders.admin import (
    CartAdmin,
    CartItemAdmin,
    OrderAdmin,
    OrderItemAdmin,
    OrderStatusHistoryAdmin,
)
from apps.products.admin import (
    CategoryAdmin,
    ProductAdmin,
    ProductImageAdmin,
    ProductReviewAdmin,
    ProductVariantAdmin,
)
from apps.users.admin import UserAdmin, UserProfileAdmin

# Get the custom user model
User = get_user_model()

# Unregister the default User admin and register our custom one
admin.site.unregister(User)

# Register all models with their custom admin classes
admin.site.register(User, UserAdmin)

# Get models from apps
UserProfile = apps.get_model("users", "UserProfile")
Category = apps.get_model("products", "Category")
Product = apps.get_model("products", "Product")
ProductImage = apps.get_model("products", "ProductImage")
ProductVariant = apps.get_model("products", "ProductVariant")
ProductReview = apps.get_model("products", "ProductReview")
Order = apps.get_model("orders", "Order")
OrderItem = apps.get_model("orders", "OrderItem")
OrderStatusHistory = apps.get_model("orders", "OrderStatusHistory")
Cart = apps.get_model("orders", "Cart")
CartItem = apps.get_model("orders", "CartItem")

# Register all models (only if not already registered)
try:
    admin.site.register(UserProfile, UserProfileAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Category, CategoryAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Product, ProductAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(ProductImage, ProductImageAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(ProductVariant, ProductVariantAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(ProductReview, ProductReviewAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Order, OrderAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(OrderItem, OrderItemAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(OrderStatusHistory, OrderStatusHistoryAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Cart, CartAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(CartItem, CartItemAdmin)
except admin.sites.AlreadyRegistered:
    pass

# Customize admin site
admin.site.site_header = "Django REST API Admin"
admin.site.site_title = "API Admin"
admin.site.index_title = "Welcome to Django REST API Administration"

# Store the original index method
original_index = admin.site.index


def custom_admin_index(request, extra_context=None):
    """
    Custom admin index with real statistics.
    """
    # Import models here to avoid circular imports
    from apps.orders.models import Order, OrderItem
    from apps.products.models import Category, Product

    # Get statistics
    user_count = User.objects.count()
    product_count = Product.objects.filter(is_active=True).count()
    category_count = Category.objects.filter(is_active=True).count()
    order_count = Order.objects.count()

    # Calculate revenue
    revenue = (
        Order.objects.filter(payment_status="paid").aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    # Recent orders
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:5]

    # Low stock products
    low_stock_products = Product.objects.filter(
        is_active=True, stock_quantity__lte=F("low_stock_threshold")
    )[:5]

    # Recent users
    recent_users = User.objects.order_by("-date_joined")[:5]

    # Prepare extra context with our data
    extra_context = extra_context or {}
    extra_context.update(
        {
            "user_count": user_count,
            "product_count": product_count,
            "category_count": category_count,
            "order_count": order_count,
            "revenue": revenue,
            "recent_orders": recent_orders,
            "low_stock_products": low_stock_products,
            "recent_users": recent_users,
        }
    )

    # Call the original index method with our extra context
    return original_index(request, extra_context)


# Override the admin site's index method
admin.site.index = custom_admin_index
