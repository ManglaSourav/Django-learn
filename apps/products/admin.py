from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Category, Product, ProductImage, ProductReview, ProductVariant


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for product images.
    """

    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "sort_order")
    readonly_fields = ("created_at", "updated_at")


class ProductVariantInline(admin.TabularInline):
    """
    Inline admin for product variants.
    """

    model = ProductVariant
    extra = 1
    fields = ("name", "sku", "price", "stock_quantity", "is_active", "attributes")


class ProductReviewInline(admin.TabularInline):
    """
    Inline admin for product reviews.
    """

    model = ProductReview
    extra = 0
    fields = (
        "user",
        "rating",
        "title",
        "comment",
        "is_approved",
        "is_verified_purchase",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category admin.
    """

    list_display = (
        "name",
        "slug",
        "parent",
        "is_active",
        "product_count",
        "created_at",
    )
    list_filter = ("is_active", "parent", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "description", "image")}),
        ("Settings", {"fields": ("is_active", "parent")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Products"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("products")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product admin.
    """

    list_display = (
        "name",
        "sku",
        "category",
        "price",
        "stock_quantity",
        "is_active",
        "is_featured",
        "is_low_stock",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "is_digital", "category", "created_at")
    search_fields = ("name", "sku", "description", "tags")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)
    inlines = [ProductImageInline, ProductVariantInline, ProductReviewInline]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "slug", "description", "short_description", "sku")},
        ),
        ("Pricing", {"fields": ("price", "compare_price", "cost_price")}),
        (
            "Inventory",
            {
                "fields": (
                    "stock_quantity",
                    "low_stock_threshold",
                    "weight",
                    "dimensions",
                )
            },
        ),
        ("Categorization", {"fields": ("category", "tags")}),
        ("Settings", {"fields": ("is_active", "is_featured", "is_digital")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    def is_low_stock(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red;">⚠️ Low Stock</span>')
        return format_html('<span style="color: green;">✓ In Stock</span>')

    is_low_stock.short_description = "Stock Status"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("images", "variants", "reviews")
        )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Product Image admin.
    """

    list_display = (
        "product",
        "image_preview",
        "alt_text",
        "is_primary",
        "sort_order",
        "created_at",
    )
    list_filter = ("is_primary", "created_at")
    search_fields = ("product__name", "alt_text")
    ordering = ("product", "sort_order", "created_at")

    fieldsets = (
        (
            "Image Information",
            {"fields": ("product", "image", "alt_text", "is_primary", "sort_order")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Preview"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    Product Variant admin.
    """

    list_display = (
        "name",
        "product",
        "sku",
        "price",
        "stock_quantity",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "product__category", "created_at")
    search_fields = ("name", "sku", "product__name")
    ordering = ("product", "name")

    fieldsets = (
        ("Basic Information", {"fields": ("product", "name", "sku")}),
        ("Pricing & Inventory", {"fields": ("price", "stock_quantity", "is_active")}),
        ("Attributes", {"fields": ("attributes",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """
    Product Review admin.
    """

    list_display = (
        "product",
        "user",
        "rating",
        "title",
        "is_approved",
        "is_verified_purchase",
        "created_at",
    )
    list_filter = ("rating", "is_approved", "is_verified_purchase", "created_at")
    search_fields = ("product__name", "user__email", "title", "comment")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Review Information",
            {"fields": ("product", "user", "rating", "title", "comment")},
        ),
        ("Status", {"fields": ("is_approved", "is_verified_purchase")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product", "user")
