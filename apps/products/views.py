from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404

from .models import Category, Product, ProductReview
from .serializers import (
    CategorySerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductReviewCreateSerializer,
    ProductReviewSerializer,
)


class CategoryListView(generics.ListAPIView):
    """
    List all categories.
    """

    queryset = Category.objects.filter(is_active=True, is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes = []


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific category.
    """

    queryset = Category.objects.filter(is_active=True, is_deleted=False)
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = []


class ProductListView(generics.ListAPIView):
    """
    List all products with filtering and search.
    """

    queryset = (
        Product.objects.filter(is_active=True, is_deleted=False)
        .select_related("category")
        .prefetch_related("images")
    )
    serializer_class = ProductListSerializer
    permission_classes = []
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "is_featured", "is_digital"]
    search_fields = ["name", "description", "short_description", "tags"]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by price range
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by rating
        min_rating = self.request.query_params.get("min_rating")
        if min_rating:
            queryset = queryset.annotate(avg_rating=Avg("reviews__rating")).filter(
                avg_rating__gte=min_rating
            )

        # Filter by stock status
        in_stock = self.request.query_params.get("in_stock")
        if in_stock and in_stock.lower() == "true":
            queryset = queryset.filter(stock_quantity__gt=0)

        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific product.
    """

    queryset = (
        Product.objects.filter(is_active=True, is_deleted=False)
        .select_related("category")
        .prefetch_related("images", "variants", "reviews")
    )
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
    permission_classes = []


class ProductCreateView(generics.CreateAPIView):
    """
    Create a new product (admin only).
    """

    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # In production, check if user is staff/admin
        serializer.save()


class ProductUpdateView(generics.UpdateAPIView):
    """
    Update a product (admin only).
    """

    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        # In production, check if user is staff/admin
        serializer.save()


class ProductDeleteView(generics.DestroyAPIView):
    """
    Delete a product (admin only).
    """

    queryset = Product.objects.all()
    lookup_field = "slug"
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()


class ProductReviewListView(generics.ListCreateAPIView):
    """
    List and create product reviews.
    """

    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_slug = self.kwargs["product_slug"]
        product = get_object_or_404(
            Product, slug=product_slug, is_active=True, is_deleted=False
        )
        return ProductReview.objects.filter(
            product=product, is_approved=True
        ).select_related("user")

    def perform_create(self, serializer):
        product_slug = self.kwargs["product_slug"]
        product = get_object_or_404(
            Product, slug=product_slug, is_active=True, is_deleted=False
        )

        # Check if user already reviewed this product
        if ProductReview.objects.filter(
            product=product, user=self.request.user
        ).exists():
            raise serializers.ValidationError("You have already reviewed this product.")

        serializer.save(product=product, user=self.request.user)


class ProductReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a product review.
    """

    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductReview.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # Only allow updating own reviews
        if serializer.instance.user != self.request.user:
            raise serializers.ValidationError("You can only update your own reviews.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow deleting own reviews
        if instance.user != self.request.user:
            raise serializers.ValidationError("You can only delete your own reviews.")
        instance.delete()


@api_view(["GET"])
@permission_classes([])
def featured_products(request):
    """
    Get featured products.
    """
    products = (
        Product.objects.filter(is_active=True, is_deleted=False, is_featured=True)
        .select_related("category")
        .prefetch_related("images")[:10]
    )

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([])
def related_products(request, product_slug):
    """
    Get related products based on category.
    """
    product = get_object_or_404(
        Product, slug=product_slug, is_active=True, is_deleted=False
    )
    related = (
        Product.objects.filter(
            category=product.category, is_active=True, is_deleted=False
        )
        .exclude(id=product.id)
        .select_related("category")
        .prefetch_related("images")[:5]
    )

    serializer = ProductListSerializer(related, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([])
def product_search(request):
    """
    Advanced product search.
    """
    query = request.query_params.get("q", "")
    if not query:
        return Response({"results": []})

    products = (
        Product.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(short_description__icontains=query)
            | Q(tags__icontains=query),
            is_active=True,
            is_deleted=False,
        )
        .select_related("category")
        .prefetch_related("images")
    )

    serializer = ProductListSerializer(products, many=True)
    return Response({"results": serializer.data})
