"""
Simple health check view to diagnose deployment issues
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import sys


def health_check(request):
    """Health check endpoint to verify deployment status"""
    status = {
        "status": "ok",
        "python_version": sys.version,
        "debug": settings.DEBUG,
        "database": "unknown",
        "database_url_set": bool(settings.DATABASES.get('default', {}).get('NAME')),
    }
    
    # Test database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "error"
    
    return JsonResponse(status)
