from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health(request):
    return Response({
        "success": True,
        "message": "Hello from Social Media Content Analyzer API"
    })
