from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for load balancers and monitoring.
    """
    return Response({
        'status': 'healthy',
        'message': 'API is running successfully',
        'version': '1.0.0'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60 * 15)  # Cache for 15 minutes
def api_info(request):
    """
    API information endpoint.
    """
    return Response({
        'name': 'Django REST API',
        'version': '1.0.0',
        'description': 'Production-ready Django REST API with comprehensive features',
        'endpoints': {
            'authentication': '/api/v1/auth/',
            'products': '/api/v1/products/',
            'orders': '/api/v1/orders/',
            'documentation': '/api/docs/',
            'health': '/health/',
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='10/m', method='GET')
def ratelimited_view(request):
    """
    Example of a rate-limited view.
    """
    return Response({
        'message': 'This view is rate limited to 10 requests per minute per IP',
        'timestamp': request.timestamp if hasattr(request, 'timestamp') else None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def server_time(request):
    """
    Get server time for client synchronization.
    """
    from django.utils import timezone
    return Response({
        'server_time': timezone.now().isoformat(),
        'timezone': str(timezone.get_current_timezone())
    })
