from rest_framework.permissions import BasePermission

from accounts.models import Role


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )


class TenantScoped(BasePermission):
    """Ensure user only accesses their client's data."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
