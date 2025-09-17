# Django REST API - Production Ready E-commerce Backend

A comprehensive, production-ready Django REST API backend system with modern e-commerce functionality, beautiful admin interface, comprehensive testing, CI/CD pipeline, and monitoring capabilities.

## 🚀 Features

### 🎯 Core Features
- **Django 4.2** with Django REST Framework 3.14
- **JWT Authentication** with refresh tokens and blacklisting
- **Custom User Model** with email-based authentication and profiles
- **Complete E-commerce System** with products, categories, orders, and cart
- **Beautiful Admin Interface** with modern UI and real-time data
- **Comprehensive API Documentation** with Swagger UI and ReDoc
- **Database Models** with soft delete, timestamps, and relationships

### 🛡️ Security & Performance
- **CORS Configuration** for cross-origin requests
- **Input Validation** and sanitization with DRF serializers
- **SQL Injection Protection** with Django ORM
- **XSS Protection** with built-in security headers
- **Database Caching** for improved performance
- **Query Optimization** with select_related and prefetch_related
- **Rate Limiting** (configurable with Redis)

### 🧪 Testing & Quality
- **Comprehensive Test Suite** with pytest and pytest-django
- **Unit Tests** for models, serializers, and views
- **Integration Tests** for API endpoints
- **Code Coverage** reporting with coverage.py
- **Code Quality Tools**: Black, Flake8, isort, Pylint
- **Pre-commit Hooks** for automated code quality
- **Factory Boy** for test data generation

### 🎨 Admin Interface
- **Modern UI Design** with custom CSS and templates
- **Real-time Dashboard** with live statistics
- **Interactive Data Tables** with sorting and filtering
- **Status Indicators** with color-coded displays
- **Quick Actions** for common tasks
- **Responsive Design** for all devices
- **Custom Branding** and navigation

### 🔧 DevOps & Monitoring
- **GitHub Actions CI/CD** pipeline with automated testing
- **Docker** containerization with multi-stage builds
- **Docker Compose** for local development
- **Nginx** reverse proxy configuration
- **Health Checks** for monitoring and load balancers
- **Prometheus Metrics** integration
- **Performance Monitoring** with Django Silk
- **Structured Logging** with different levels

### 📊 Database & Storage
- **SQLite** for development (easily switchable to PostgreSQL)
- **Database Migrations** with proper versioning
- **File Storage** with AWS S3 support
- **Image Handling** with Pillow
- **Data Management** with sample data loading

## 📋 Requirements

- Python 3.9+
- SQLite (default) or PostgreSQL 15+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd new_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py load_sample_data
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Development

1. **Start services**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py create_superuser
   ```

4. **Load sample data**
   ```bash
   docker-compose exec web python manage.py load_sample_data
   ```

## 🎨 Admin Interface

### Access Admin Panel
- **URL**: http://localhost:8000/admin/
- **Username**: admin@example.com
- **Password**: admin

### Admin Features
- **Modern Dashboard** with real-time statistics
- **User Management** with custom user model
- **Product Management** with categories, variants, and reviews
- **Order Management** with status tracking and history
- **Cart Management** for shopping cart functionality
- **Quick Actions** for common administrative tasks
- **API Documentation** links for easy access

### Dashboard Statistics
- **Total Users**: Real count from database
- **Products**: Active products count
- **Orders**: Total orders count
- **Revenue**: Calculated from paid orders
- **Recent Activity**: Live order updates
- **Quick Actions**: Direct links to add new records

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run specific test types
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With specific markers
pytest -m "not slow"
```

## 🔧 Code Quality

### Format code
```bash
black .
isort .
```

### Lint code
```bash
flake8 .
pylint apps/ config/
```

### Run pre-commit hooks
```bash
pre-commit install
pre-commit run --all-files
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **Admin Panel**: http://localhost:8000/admin/

## 🚀 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login with JWT
- `POST /api/v1/auth/logout/` - User logout (blacklist token)
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `GET /api/v1/auth/profile/` - Get user profile
- `PUT /api/v1/auth/profile/` - Update user profile
- `POST /api/v1/auth/change-password/` - Change password
- `POST /api/v1/auth/password-reset/` - Request password reset
- `POST /api/v1/auth/password-reset-confirm/` - Confirm password reset

### Products
- `GET /api/v1/products/` - List products with filtering
- `GET /api/v1/products/{id}/` - Get product details
- `GET /api/v1/products/categories/` - List categories
- `GET /api/v1/products/featured/` - Get featured products
- `GET /api/v1/products/search/` - Search products
- `GET /api/v1/products/{id}/reviews/` - Get product reviews
- `POST /api/v1/products/{id}/reviews/` - Create product review

### Orders
- `GET /api/v1/orders/` - List user orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/{id}/` - Get order details
- `PUT /api/v1/orders/{id}/` - Update order
- `DELETE /api/v1/orders/{id}/` - Cancel order
- `GET /api/v1/orders/{id}/status-history/` - Get order status history

### Cart Management
- `GET /api/v1/orders/cart/` - Get user cart
- `PUT /api/v1/orders/cart/` - Update cart
- `DELETE /api/v1/orders/cart/` - Clear cart
- `GET /api/v1/orders/cart/items/` - List cart items
- `POST /api/v1/orders/cart/items/` - Add item to cart
- `PUT /api/v1/orders/cart/items/{id}/` - Update cart item
- `DELETE /api/v1/orders/cart/items/{id}/` - Remove cart item
- `POST /api/v1/orders/checkout/` - Checkout cart to order

### Core
- `GET /api/v1/core/health/` - Health check
- `GET /api/v1/core/info/` - API information
- `GET /api/v1/core/time/` - Server time

## 🏗️ Project Structure

```
new_project/
├── apps/
│   ├── core/                    # Core functionality
│   │   ├── admin.py            # Custom admin configurations
│   │   ├── admin_views.py      # Custom admin views
│   │   ├── models.py           # Base models (TimeStamped, SoftDelete)
│   │   ├── serializers.py      # Base serializers
│   │   ├── views.py            # Core API views
│   │   ├── urls.py             # Core URL patterns
│   │   └── management/
│   │       └── commands/
│   │           ├── create_superuser.py
│   │           └── load_sample_data.py
│   ├── users/                   # User management
│   │   ├── admin.py            # User admin interface
│   │   ├── models.py           # User and UserProfile models
│   │   ├── serializers.py      # User serializers
│   │   ├── views.py            # Authentication views
│   │   └── urls.py             # User URL patterns
│   ├── products/                # Product management
│   │   ├── admin.py            # Product admin interface
│   │   ├── models.py           # Product, Category, Review models
│   │   ├── serializers.py      # Product serializers
│   │   ├── views.py            # Product API views
│   │   └── urls.py             # Product URL patterns
│   └── orders/                  # Order management
│       ├── admin.py            # Order admin interface
│       ├── models.py           # Order, Cart models
│       ├── serializers.py      # Order serializers
│       ├── views.py            # Order API views
│       └── urls.py             # Order URL patterns
├── config/                      # Django settings
│   ├── settings.py             # Main settings
│   ├── urls.py                 # Main URL configuration
│   ├── wsgi.py                 # WSGI configuration
│   └── asgi.py                 # ASGI configuration
├── templates/                   # Custom templates
│   └── admin/                  # Admin templates
│       ├── base.html           # Base admin template
│       ├── index.html          # Admin dashboard
│       ├── change_list.html    # List view template
│       └── change_form.html    # Form template
├── static/                      # Static files
│   └── admin/                  # Admin static files
│       ├── css/
│       │   └── custom-admin.css # Custom admin styles
│       └── img/
│           └── logo.svg        # Admin logo
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── conftest.py             # Test configuration
│   └── fixtures/               # Test fixtures
├── .github/                     # GitHub Actions
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline
├── docker-compose.yml           # Docker Compose
├── Dockerfile                   # Docker configuration
├── requirements.txt             # Python dependencies
├── admin.py                     # Admin configuration
└── README.md                    # This file
```

## 🎨 Admin Interface Features

### Modern Dashboard
- **Real-time Statistics**: Live data from database
- **Interactive Cards**: Hover effects and animations
- **Quick Actions**: Direct links to common tasks
- **Recent Activity**: Live order and user updates
- **Responsive Design**: Works on all devices

### Enhanced Data Management
- **Custom Admin Classes**: Optimized for each model
- **Inline Editing**: Related models in same view
- **Status Indicators**: Color-coded status displays
- **Image Previews**: Product and user image thumbnails
- **Search & Filtering**: Advanced search capabilities
- **Bulk Actions**: Mass operations on records

### Visual Improvements
- **Custom CSS**: Modern styling with gradients and shadows
- **Font Awesome Icons**: Professional iconography
- **Color Coding**: Status-based color schemes
- **Smooth Animations**: Hover effects and transitions
- **Custom Logo**: Branded admin interface
- **Navigation Links**: Direct access to API docs

## 🔒 Security Features

- **JWT Authentication** with secure token handling
- **Password Validation** with Django's built-in validators
- **CORS Protection** with configurable origins
- **Input Sanitization** and validation
- **SQL Injection Protection** with Django ORM
- **XSS Protection** with security headers
- **CSRF Protection** for state-changing operations
- **Rate Limiting** to prevent abuse (configurable)

## 📊 Monitoring & Logging

- **Health Checks** for load balancer integration
- **Prometheus Metrics** for monitoring
- **Structured Logging** with different levels
- **Performance Profiling** with Django Silk
- **Error Tracking** with comprehensive logging
- **Database Query Monitoring** with Silk

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**
   - Set `DEBUG=False`
   - Configure `SECRET_KEY`
   - Set up database credentials
   - Configure email settings
   - Set up AWS S3 (optional)

2. **Database**
   - Run migrations
   - Create superuser
   - Load sample data (optional)
   - Set up database backups

3. **Static Files**
   - Collect static files
   - Configure static file serving
   - Set up CDN (optional)

4. **Security**
   - Set up HTTPS
   - Configure CORS origins
   - Set up rate limiting
   - Enable security headers

5. **Monitoring**
   - Set up health checks
   - Configure logging
   - Set up error tracking
   - Monitor performance

### Docker Production

```bash
# Build production image
docker build -t django-rest-api .

# Run with production settings
docker run -d \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -p 8000:8000 \
  django-rest-api
```

## 🧪 Sample Data

The system includes a comprehensive sample data loader:

```bash
python manage.py load_sample_data
```

**Sample Data Includes:**
- **5 Categories**: Electronics, Clothing, Books, Home & Garden, Sports
- **6 Products**: iPhone, Samsung Galaxy, Nike Shoes, Python Book, Garden Tools, Yoga Mat
- **9 Product Variants**: Colors and sizes for products
- **16 Product Reviews**: User reviews with ratings
- **10 Orders**: Complete order history with items
- **4 Users**: Test users with profiles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the admin panel
- Check the test suite for examples

## 🔄 Changelog

### v1.0.0 - Complete E-commerce Backend
- ✅ **Complete Django REST API** with authentication
- ✅ **E-commerce System** with products, orders, and cart
- ✅ **Beautiful Admin Interface** with modern UI
- ✅ **Comprehensive Testing** suite with pytest
- ✅ **CI/CD Pipeline** with GitHub Actions
- ✅ **Docker Support** with multi-stage builds
- ✅ **API Documentation** with Swagger UI
- ✅ **Sample Data** loading system
- ✅ **Code Quality** tools and pre-commit hooks
- ✅ **Monitoring** with health checks and metrics

## 🎯 Key Achievements

- **Production-Ready**: Complete with security, testing, and monitoring
- **Modern UI**: Beautiful admin interface with real-time data
- **Comprehensive API**: Full e-commerce functionality
- **Developer Experience**: Excellent documentation and tooling
- **Scalable Architecture**: Clean, maintainable code structure
- **Quality Assurance**: Comprehensive testing and code quality tools