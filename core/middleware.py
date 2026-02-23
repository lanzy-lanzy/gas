import time
import logging
from django.conf import settings
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('core.performance')


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor page load times and database query performance
    Requirements: 9.1, 9.2, 9.3 - Performance optimization and monitoring
    """
    
    def process_request(self, request):
        """Start timing the request"""
        request._start_time = time.time()
        request._queries_before = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """Log performance metrics"""
        if hasattr(request, '_start_time'):
            # Calculate request duration
            duration = time.time() - request._start_time
            
            # Count database queries
            queries_count = len(connection.queries) - getattr(request, '_queries_before', 0)
            
            # Log slow requests (> 1 second)
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s with {queries_count} queries"
                )
            
            # Log requests with many queries (potential N+1 problem)
            if queries_count > 10:
                logger.warning(
                    f"High query count: {request.method} {request.path} "
                    f"executed {queries_count} queries in {duration:.2f}s"
                )
            
            # Add performance headers for debugging
            if settings.DEBUG:
                response['X-Response-Time'] = f"{duration:.3f}s"
                response['X-Query-Count'] = str(queries_count)
        
        return response


class MobileOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware to optimize responses for mobile devices
    Requirements: 9.5 - Mobile optimization for low-end smartphones
    """
    
    def process_request(self, request):
        """Detect mobile devices and connection quality"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Simple mobile detection
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'tablet', 'phone']
        request.is_mobile = any(keyword in user_agent for keyword in mobile_keywords)
        
        # Detect slow connections (simplified)
        connection_header = request.META.get('HTTP_CONNECTION', '').lower()
        request.is_slow_connection = 'slow' in connection_header or '2g' in connection_header
        
        return None
    
    def process_response(self, request, response):
        """Add mobile optimization headers"""
        if hasattr(request, 'is_mobile') and request.is_mobile:
            # Add cache headers for mobile
            response['Cache-Control'] = 'public, max-age=300'  # 5 minutes
            
            # Add compression hint
            response['Vary'] = 'Accept-Encoding, User-Agent'
            
            # Add mobile-specific headers
            response['X-Mobile-Optimized'] = 'true'
        
        if hasattr(request, 'is_slow_connection') and request.is_slow_connection:
            # Extend cache time for slow connections
            response['Cache-Control'] = 'public, max-age=600'  # 10 minutes
            response['X-Slow-Connection-Optimized'] = 'true'
        
        return response


class CacheOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware to add intelligent caching headers
    Requirements: 9.2 - Caching for frequently accessed data
    """
    
    # Define cache durations for different URL patterns
    CACHE_PATTERNS = {
        '/static/': 86400,  # 24 hours for static files
        '/media/': 86400,   # 24 hours for media files
        '/api/': 300,       # 5 minutes for API endpoints
        '/dealer/dashboard/': 30,  # 30 seconds for dashboard
        '/customer/dashboard/': 60,  # 1 minute for customer dashboard
    }
    
    def process_response(self, request, response):
        """Add appropriate cache headers based on URL patterns"""
        if response.status_code == 200:
            path = request.path
            
            # Find matching cache pattern
            cache_duration = None
            for pattern, duration in self.CACHE_PATTERNS.items():
                if path.startswith(pattern):
                    cache_duration = duration
                    break
            
            # Apply cache headers
            if cache_duration:
                response['Cache-Control'] = f'public, max-age={cache_duration}'
                
                # Add ETag for better caching
                if not response.get('ETag') and not getattr(response, 'streaming', False) and hasattr(response, 'content'):
                    import hashlib
                    content_hash = hashlib.md5(response.content).hexdigest()[:8]
                    response['ETag'] = f'"{content_hash}"'
        
        return response