"""Role-based permissions matching Spring Boot @PreAuthorize annotations."""

from rest_framework.permissions import BasePermission


class IsVillager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'VILLAGER'


class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'FARMER'


class IsPanchayatAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'PANCHAYAT_ADMIN'


class IsVillagerFarmerOrAdmin(BasePermission):
    """VILLAGER, FARMER, or PANCHAYAT_ADMIN — used for grievances, equipment, etc."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'VILLAGER', 'FARMER', 'PANCHAYAT_ADMIN'
        )


class IsAnyAuthenticated(BasePermission):
    """Any authenticated user with any role."""
    def has_permission(self, request, view):
        return request.user.is_authenticated
