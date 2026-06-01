from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "endpoints": {
            "auth": "/api/v1/auth/register/, /api/v1/auth/login/, /api/v1/auth/me/",
            "listings": "/api/v1/listings/",
            "bookings": "/api/v1/bookings/",
            "payments": "/api/v1/payments/initiate/"
        }
    })