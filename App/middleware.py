from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured
import logging

class DatabaseHealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Test database connection
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            response = self.get_response(request)
            return response
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Database connection failed: {str(e)}")
            
            # Return a user-friendly error page
            if request.path.startswith('/accounts/'):
                return HttpResponse("""
                <div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
                    <h1>Service Temporarily Unavailable</h1>
                    <p>We're experiencing technical difficulties. Please try again in a few minutes.</p>
                    <p><a href="/">Return to Homepage</a></p>
                </div>
                """, status=503)
            
            return HttpResponse("Service Unavailable", status=503)
