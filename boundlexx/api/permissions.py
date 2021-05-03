from rest_framework import permissions


class IsWorldTrusted(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        return request.user.has_perm("boundless.is_trusted_user")
