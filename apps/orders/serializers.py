from rest_framework import serializers

from django.db import transaction

from apps.core.serializers import TimeStampedSerializer
from apps.products.serializers import ProductListSerializer, ProductVariantSerializer

from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(TimeStampedSerializer):
    """
    Order item serializer.
    """

    product = ProductListSerializer(read_only=True)
    product_variant = ProductVariantSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    product_variant_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_id",
            "product_variant",
            "product_variant_id",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "unit_price",
            "total_price",
            "created_at",
            "updated_at",
        )


class OrderSerializer(TimeStampedSerializer):
    """
    Order serializer.
    """

    items = OrderItemSerializer(many=True, read_only=True)
    billing_full_name = serializers.ReadOnlyField()
    shipping_full_name = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    can_be_refunded = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "status",
            "payment_status",
            "subtotal",
            "tax_amount",
            "shipping_amount",
            "discount_amount",
            "total_amount",
            "billing_first_name",
            "billing_last_name",
            "billing_full_name",
            "billing_email",
            "billing_phone",
            "billing_address_line_1",
            "billing_address_line_2",
            "billing_city",
            "billing_state",
            "billing_postal_code",
            "billing_country",
            "shipping_first_name",
            "shipping_last_name",
            "shipping_full_name",
            "shipping_phone",
            "shipping_address_line_1",
            "shipping_address_line_2",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
            "shipping_country",
            "notes",
            "tracking_number",
            "shipped_at",
            "delivered_at",
            "items",
            "can_be_cancelled",
            "can_be_refunded",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "order_number",
            "subtotal",
            "tax_amount",
            "shipping_amount",
            "discount_amount",
            "total_amount",
            "shipped_at",
            "delivered_at",
            "created_at",
            "updated_at",
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Order creation serializer.
    """

    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
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
            "shipping_first_name",
            "shipping_last_name",
            "shipping_phone",
            "shipping_address_line_1",
            "shipping_address_line_2",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
            "shipping_country",
            "notes",
            "items",
        )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        with transaction.atomic():
            # Calculate totals
            subtotal = 0
            for item_data in items_data:
                product_id = item_data["product_id"]
                quantity = item_data["quantity"]

                from apps.products.models import Product, ProductVariant

                try:
                    product = Product.objects.get(
                        id=product_id, is_active=True, is_deleted=False
                    )
                except Product.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Product with id {product_id} not found."
                    )

                # Get unit price
                if (
                    "product_variant_id" in item_data
                    and item_data["product_variant_id"]
                ):
                    try:
                        variant = ProductVariant.objects.get(
                            id=item_data["product_variant_id"],
                            product=product,
                            is_active=True,
                        )
                        unit_price = variant.price
                    except ProductVariant.DoesNotExist:
                        raise serializers.ValidationError(f"Product variant not found.")
                else:
                    unit_price = product.price

                item_total = quantity * unit_price
                subtotal += item_total

                # Check stock
                if product.stock_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}."
                    )

            # Calculate other amounts (simplified)
            tax_amount = subtotal * 0.1  # 10% tax
            shipping_amount = 10.00  # Fixed shipping
            discount_amount = 0.00
            total_amount = subtotal + tax_amount + shipping_amount - discount_amount

            # Create order
            order = Order.objects.create(
                user=user,
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_amount=shipping_amount,
                discount_amount=discount_amount,
                total_amount=total_amount,
                **validated_data,
            )

            # Create order items
            for item_data in items_data:
                product_id = item_data["product_id"]
                quantity = item_data["quantity"]

                product = Product.objects.get(id=product_id)

                if (
                    "product_variant_id" in item_data
                    and item_data["product_variant_id"]
                ):
                    variant = ProductVariant.objects.get(
                        id=item_data["product_variant_id"], product=product
                    )
                    unit_price = variant.price
                else:
                    unit_price = product.price

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_variant=variant
                    if "product_variant_id" in item_data
                    and item_data["product_variant_id"]
                    else None,
                    quantity=quantity,
                    unit_price=unit_price,
                )

                # Update stock
                product.stock_quantity -= quantity
                product.save()

            return order


class OrderStatusHistorySerializer(TimeStampedSerializer):
    """
    Order status history serializer.
    """

    changed_by_email = serializers.CharField(source="changed_by.email", read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = (
            "id",
            "status",
            "notes",
            "changed_by",
            "changed_by_email",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CartItemSerializer(TimeStampedSerializer):
    """
    Cart item serializer.
    """

    product = ProductListSerializer(read_only=True)
    product_variant = ProductVariantSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    product_variant_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "product_id",
            "product_variant",
            "product_variant_id",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "unit_price",
            "total_price",
            "created_at",
            "updated_at",
        )


class CartSerializer(TimeStampedSerializer):
    """
    Cart serializer.
    """

    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "items",
            "total_items",
            "total_amount",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Cart item creation serializer.
    """

    class Meta:
        model = CartItem
        fields = ("product_id", "product_variant_id", "quantity")

    def validate(self, attrs):
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity")

        from apps.products.models import Product, ProductVariant

        try:
            product = Product.objects.get(
                id=product_id, is_active=True, is_deleted=False
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")

        if product.stock_quantity < quantity:
            raise serializers.ValidationError("Insufficient stock.")

        return attrs

    def create(self, validated_data):
        cart = self.context["cart"]
        product_id = validated_data["product_id"]
        quantity = validated_data["quantity"]

        from apps.products.models import Product, ProductVariant

        product = Product.objects.get(id=product_id)

        # Get unit price
        if (
            "product_variant_id" in validated_data
            and validated_data["product_variant_id"]
        ):
            variant = ProductVariant.objects.get(
                id=validated_data["product_variant_id"], product=product, is_active=True
            )
            unit_price = variant.price
        else:
            unit_price = product.price

        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            product_variant=variant
            if "product_variant_id" in validated_data
            and validated_data["product_variant_id"]
            else None,
            defaults={"quantity": quantity, "unit_price": unit_price},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item
