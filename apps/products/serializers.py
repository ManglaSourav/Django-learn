from rest_framework import serializers
from django.db.models import Avg
from .models import Category, Product, ProductImage, ProductVariant, ProductReview
from apps.core.serializers import TimeStampedSerializer


class CategorySerializer(TimeStampedSerializer):
    """
    Category serializer.
    """
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'image', 'is_active',
            'parent', 'children', 'product_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True, is_deleted=False).count()


class ProductImageSerializer(TimeStampedSerializer):
    """
    Product image serializer.
    """
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'sort_order', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductVariantSerializer(TimeStampedSerializer):
    """
    Product variant serializer.
    """
    class Meta:
        model = ProductVariant
        fields = (
            'id', 'name', 'sku', 'price', 'stock_quantity', 'is_active',
            'attributes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductReviewSerializer(TimeStampedSerializer):
    """
    Product review serializer.
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = ProductReview
        fields = (
            'id', 'user', 'user_name', 'user_email', 'rating', 'title', 'comment',
            'is_approved', 'is_verified_purchase', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class ProductListSerializer(TimeStampedSerializer):
    """
    Product list serializer for listing views.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    discount_percentage = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'short_description', 'sku', 'price', 'compare_price',
            'stock_quantity', 'category', 'category_name', 'is_active', 'is_featured',
            'primary_image', 'average_rating', 'review_count', 'discount_percentage',
            'is_low_stock', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None

    def get_average_rating(self, obj):
        avg_rating = obj.reviews.filter(is_approved=True).aggregate(avg_rating=Avg('rating'))
        return round(avg_rating['avg_rating'] or 0, 2)

    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductDetailSerializer(TimeStampedSerializer):
    """
    Product detail serializer for detail views.
    """
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    discount_percentage = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'short_description', 'sku', 'price',
            'compare_price', 'cost_price', 'stock_quantity', 'low_stock_threshold',
            'weight', 'dimensions', 'category', 'is_active', 'is_featured', 'is_digital',
            'tags', 'meta_title', 'meta_description', 'images', 'variants', 'reviews',
            'average_rating', 'review_count', 'discount_percentage', 'is_low_stock',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_average_rating(self, obj):
        avg_rating = obj.reviews.filter(is_approved=True).aggregate(avg_rating=Avg('rating'))
        return round(avg_rating['avg_rating'] or 0, 2)

    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductCreateUpdateSerializer(TimeStampedSerializer):
    """
    Product create/update serializer.
    """
    class Meta:
        model = Product
        fields = (
            'name', 'description', 'short_description', 'sku', 'price', 'compare_price',
            'cost_price', 'stock_quantity', 'low_stock_threshold', 'weight', 'dimensions',
            'category', 'is_active', 'is_featured', 'is_digital', 'tags', 'meta_title',
            'meta_description'
        )

    def validate_sku(self, value):
        if self.instance and self.instance.sku == value:
            return value
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value


class ProductReviewCreateSerializer(serializers.ModelSerializer):
    """
    Product review creation serializer.
    """
    class Meta:
        model = ProductReview
        fields = ('rating', 'title', 'comment')

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
