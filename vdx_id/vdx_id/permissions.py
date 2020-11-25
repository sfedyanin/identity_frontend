from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
            return obj.owner == request.user

class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
            if request.user.is_staff:
                return True
            else:
                return obj.owner == request.user