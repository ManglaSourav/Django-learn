from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    """
    Inline admin for order items.
    """

    model = OrderItem
    extra = 0
    fields = ("product", "product_variant", "quantity", "unit_price", "total_price")
    readonly_fields = ("total_price", "created_at", "updated_at")


class OrderStatusHistoryInline(admin.TabularInline):
    """
    Inline admin for order status history.
    """

    model = OrderStatusHistory
    extra = 0
    fields = ("status", "notes", "changed_by", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order admin.
    """

    list_display = (
        "order_number",
        "user",
        "status",
        "payment_status",
        "total_amount",
        "billing_full_name",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "created_at",
        "shipped_at",
        "delivered_at",
    )
    search_fields = (
        "order_number",
        "user__email",
        "billing_first_name",
        "billing_last_name",
        "billing_email",
    )
    ordering = ("-created_at",)
    inlines = [OrderItemInline, OrderStatusHistoryInline]

    fieldsets = (
        (
            "Order Information",
            {"fields": ("order_number", "user", "status", "payment_status")},
        ),
        (
            "Pricing",
            {
                "fields": (
                    "subtotal",
                    "tax_amount",
                    "shipping_amount",
                    "discount_amount",
                    "total_amount",
                )
            },
        ),
        (
            "Billing Information",
            {
                "fields": (
                    "billing_first_name",
                    "billing_last_name",
                    "billing_email",
                    "billing_phone",
                    "billing_address_line_1",
                    "billing_address_line_2",
                    "billing_city",
                    "billing_state",
                    "billing_postal_code",
                    "billing_country",
                )
            },
        ),
        (
            "Shipping Information",
            {
                "fields": (
                    "shipping_first_name",
                    "shipping_last_name",
                    "shipping_phone",
                    "shipping_address_line_1",
                    "shipping_address_line_2",
                    "shipping_city",
                    "shipping_state",
                    "shipping_postal_code",
                    "shipping_country",
                )
            },
        ),
        (
            "Additional Information",
            {"fields": ("notes", "tracking_number", "shipped_at", "delivered_at")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("order_number", "created_at", "updated_at")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related(
                "items__product", "items__product_variant", "status_history__changed_by"
            )
        )

    def save_model(self, request, obj, form, change):
        if not change:  # New order
            obj.user = request.user
        super().save_model(request, obj, form, change)

        # Create status history entry if status changed
        if change and "status" in form.changed_data:
            OrderStatusHistory.objects.create(
                order=obj,
                status=obj.status,
                notes=f"Status changed to {obj.status}",
                changed_by=request.user,
            )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Order Item admin.
    """

    list_display = (
        "order",
        "product",
        "product_variant",
        "quantity",
        "unit_price",
        "total_price",
        "created_at",
    )
    list_filter = ("order__status", "created_at")
    search_fields = ("order__order_number", "product__name", "product_variant__name")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Item Information",
            {
                "fields": (
                    "order",
                    "product",
                    "product_variant",
                    "quantity",
                    "unit_price",
                    "total_price",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("total_price", "created_at", "updated_at")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("order", "product", "product_variant")
        )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """
    Order Status History admin.
    """

    list_display = ("order", "status", "changed_by", "notes", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__order_number", "changed_by__email", "notes")
    ordering = ("-created_at",)

    fieldsets = (
        ("Status Information", {"fields": ("order", "status", "notes", "changed_by")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order", "changed_by")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Cart admin.
    """

    list_display = ("user", "total_items", "total_amount", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email",)
    ordering = ("-created_at",)

    fieldsets = (
        ("Cart Information", {"fields": ("user", "session_key")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("items__product", "items__product_variant")
        )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Cart Item admin.
    """

    list_display = (
        "cart",
        "product",
        "product_variant",
        "quantity",
        "unit_price",
        "total_price",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("cart__user__email", "product__name", "product_variant__name")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Item Information",
            {
                "fields": (
                    "cart",
                    "product",
                    "product_variant",
                    "quantity",
                    "unit_price",
                    "total_price",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("total_price", "created_at", "updated_at")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("cart__user", "product", "product_variant")
        )
