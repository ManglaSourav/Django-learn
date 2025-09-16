from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Products
    path('', views.ProductListView.as_view(), name='product-list'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<slug:slug>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    
    # Product reviews
    path('<slug:product_slug>/reviews/', views.ProductReviewListView.as_view(), name='product-review-list'),
    path('reviews/<int:pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),
    
    # Special endpoints
    path('featured/', views.featured_products, name='featured-products'),
    path('<slug:slug>/related/', views.related_products, name='related-products'),
    path('search/', views.product_search, name='product-search'),
]
