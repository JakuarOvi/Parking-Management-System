from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Check if user is an admin."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'Admin'


class IsAdminOrStaff(BasePermission):
    """Check if user is admin or staff."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['Admin', 'Staff']
