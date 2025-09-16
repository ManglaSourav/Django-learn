# Django REST API - Production Ready Backend System

A comprehensive, production-ready Django REST API backend system with authentication, e-commerce functionality, testing, CI/CD, and monitoring.

## 🚀 Features

### Core Features
- **Django 4.2** with Django REST Framework
- **JWT Authentication** with refresh tokens
- **Custom User Model** with profile management
- **E-commerce System** with products, orders, and cart
- **Comprehensive API Documentation** with Swagger/OpenAPI
- **Database Models** with soft delete and timestamps

### Security & Performance
- **CORS Configuration** for cross-origin requests
- **Rate Limiting** to prevent abuse
- **Input Validation** and sanitization
- **SQL Injection Protection** with Django ORM
- **XSS Protection** with built-in security headers
- **Redis Caching** for improved performance
- **Database Query Optimization** with select_related and prefetch_related

### Testing & Quality
- **Comprehensive Test Suite** with pytest
- **Unit Tests** for models, serializers, and views
- **Integration Tests** for API endpoints
- **Code Coverage** reporting
- **Code Quality Tools**: Black, Flake8, isort, Pylint
- **Pre-commit Hooks** for code quality
- **Security Scanning** with Bandit and Safety

### DevOps & Monitoring
- **GitHub Actions CI/CD** pipeline
- **Docker** containerization with multi-stage builds
- **Docker Compose** for local development
- **Nginx** reverse proxy configuration
- **Health Checks** for monitoring
- **Prometheus Metrics** integration
- **Sentry** error tracking (optional)
- **Performance Monitoring** with Silk (development)

### Database & Caching
- **PostgreSQL** as primary database
- **Redis** for caching and session storage
- **Database Migrations** with proper versioning
- **Connection Pooling** for better performance

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-rest-api
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


## 🚀 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `GET /api/v1/auth/profile/` - Get user profile
- `PUT /api/v1/auth/profile/` - Update user profile
- `POST /api/v1/auth/change-password/` - Change password

### Products
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/{slug}/` - Get product details
- `GET /api/v1/products/categories/` - List categories
- `GET /api/v1/products/featured/` - Get featured products
- `GET /api/v1/products/search/` - Search products

### Orders
- `GET /api/v1/orders/` - List user orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/{id}/` - Get order details
- `GET /api/v1/orders/cart/` - Get cart
- `POST /api/v1/orders/cart/add/` - Add item to cart
- `POST /api/v1/orders/checkout/` - Checkout cart

### Core
- `GET /api/v1/core/health/` - Health check
- `GET /api/v1/core/info/` - API information
- `GET /api/v1/core/time/` - Server time

## 🏗️ Project Structure

```
django-rest-api/
├── apps/
│   ├── core/           # Core functionality
│   ├── users/          # User management
│   ├── products/       # Product management
│   └── orders/         # Order management
├── config/             # Django settings
├── tests/              # Test suite
├── static/             # Static files
├── media/              # Media files
├── logs/               # Log files
├── .github/            # GitHub Actions
├── docker-compose.yml  # Docker Compose
├── Dockerfile          # Docker configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔒 Security Features

- **JWT Authentication** with secure token handling
- **Password Validation** with Django's built-in validators
- **CORS Protection** with configurable origins
- **Rate Limiting** to prevent abuse
- **Input Sanitization** and validation
- **SQL Injection Protection** with Django ORM
- **XSS Protection** with security headers
- **CSRF Protection** for state-changing operations

## 📊 Monitoring & Logging

- **Health Checks** for load balancer integration
- **Prometheus Metrics** for monitoring
- **Structured Logging** with different levels
- **Error Tracking** with Sentry (optional)
- **Performance Profiling** with Silk (development)

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**
   - Set `DEBUG=False`
   - Configure `SECRET_KEY`
   - Set up database credentials
   - Configure Redis URL
   - Set up email settings

2. **Database**
   - Run migrations
   - Create superuser
   - Set up database backups

3. **Static Files**
   - Collect static files
   - Configure static file serving

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
  -e DATABASE_URL=postgresql://user:pass@host:port/db \
  -p 8000:8000 \
  django-rest-api
```

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
- Check the documentation
- Review the API documentation

## 🔄 Changelog

### v1.0.0
- Initial release
- Complete e-commerce API
- Authentication system
- Testing suite
- CI/CD pipeline
- Docker support
- Documentation
