from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelfOrAdmin(BasePermission):
    """
    Users can view/update themselves; admins can do anything.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS and obj == request.user:
            return True
        return request.user.is_staff or obj == request.user
