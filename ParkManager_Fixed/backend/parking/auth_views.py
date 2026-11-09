from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Clear the authenticated Django session."""
    logout(request)
    return Response({"message": "Logged out successfully"})
