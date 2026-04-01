from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']

class IsAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        # Les agents ont accès, mais on pourra restreindre certaines méthodes (POST/DELETE) dans les ViewSets
        return request.user.is_authenticated and request.user.role in ['agent', 'admin', 'superadmin']

class IsMFAIncomplete(permissions.BasePermission):
    """
    Autorise l'accès uniquement si l'utilisateur doit encore configurer son MFA.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and not request.user.is_mfa_enabled