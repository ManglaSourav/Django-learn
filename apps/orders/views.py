from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory
from .serializers import (
    CartItemCreateSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusHistorySerializer,
)


class OrderListView(generics.ListCreateAPIView):
    """
    List and create orders.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product"
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an order.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product"
        )

    def perform_update(self, serializer):
        # Only allow updating certain fields
        allowed_fields = ["notes", "shipping_address_line_1", "shipping_address_line_2"]
        for field in allowed_fields:
            if field in serializer.validated_data:
                setattr(serializer.instance, field, serializer.validated_data[field])
        serializer.instance.save()

    def perform_destroy(self, instance):
        # Only allow cancelling orders that can be cancelled
        if instance.can_be_cancelled():
            instance.status = "cancelled"
            instance.save()

            # Create status history entry
            OrderStatusHistory.objects.create(
                order=instance,
                status="cancelled",
                notes="Order cancelled by user",
                changed_by=self.request.user,
            )
        else:
            raise serializers.ValidationError("This order cannot be cancelled.")


class OrderStatusHistoryView(generics.ListAPIView):
    """
    List order status history.
    """

    serializer_class = OrderStatusHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs["order_id"]
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        return OrderStatusHistory.objects.filter(order=order)


class CartView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or clear cart.
    """

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def perform_destroy(self, instance):
        # Clear all cart items
        instance.items.all().delete()


class CartItemListView(generics.ListCreateAPIView):
    """
    List and add cart items.
    """

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related(
            "product", "product_variant"
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CartItemCreateSerializer
        return CartItemSerializer

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a cart item.
    """

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related(
            "product", "product_variant"
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Add item to cart.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartItemCreateSerializer(data=request.data, context={"cart": cart})

    if serializer.is_valid():
        cart_item = serializer.save()
        return Response(
            CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """
    Remove item from cart.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return Response({"message": "Item removed from cart."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_cart_item_quantity(request, item_id):
    """
    Update cart item quantity.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    quantity = request.data.get("quantity")
    if not quantity or quantity < 1:
        return Response(
            {"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST
        )

    if cart_item.product.stock_quantity < quantity:
        return Response(
            {"error": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST
        )

    cart_item.quantity = quantity
    cart_item.save()

    return Response(CartItemSerializer(cart_item).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """
    Clear all items from cart.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    return Response({"message": "Cart cleared."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    """
    Convert cart to order.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)

    if not cart.items.exists():
        return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

    # Create order from cart
    order_data = {
        "billing_first_name": request.data.get("billing_first_name", ""),
        "billing_last_name": request.data.get("billing_last_name", ""),
        "billing_email": request.data.get("billing_email", ""),
        "billing_phone": request.data.get("billing_phone", ""),
        "billing_address_line_1": request.data.get("billing_address_line_1", ""),
        "billing_address_line_2": request.data.get("billing_address_line_2", ""),
        "billing_city": request.data.get("billing_city", ""),
        "billing_state": request.data.get("billing_state", ""),
        "billing_postal_code": request.data.get("billing_postal_code", ""),
        "billing_country": request.data.get("billing_country", ""),
        "shipping_first_name": request.data.get("shipping_first_name", ""),
        "shipping_last_name": request.data.get("shipping_last_name", ""),
        "shipping_phone": request.data.get("shipping_phone", ""),
        "shipping_address_line_1": request.data.get("shipping_address_line_1", ""),
        "shipping_address_line_2": request.data.get("shipping_address_line_2", ""),
        "shipping_city": request.data.get("shipping_city", ""),
        "shipping_state": request.data.get("shipping_state", ""),
        "shipping_postal_code": request.data.get("shipping_postal_code", ""),
        "shipping_country": request.data.get("shipping_country", ""),
        "notes": request.data.get("notes", ""),
        "items": [],
    }

    # Convert cart items to order items
    for cart_item in cart.items.all():
        order_item_data = {
            "product_id": cart_item.product.id,
            "quantity": cart_item.quantity,
        }
        if cart_item.product_variant:
            order_item_data["product_variant_id"] = cart_item.product_variant.id
        order_data["items"].append(order_item_data)

    serializer = OrderCreateSerializer(data=order_data, context={"request": request})

    if serializer.is_valid():
        with transaction.atomic():
            order = serializer.save()

            # Clear cart after successful order creation
            cart.items.all().delete()

            # Create initial status history
            OrderStatusHistory.objects.create(
                order=order,
                status="pending",
                notes="Order created",
                changed_by=request.user,
            )

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
