"""AgriTech models — Equipment, EquipmentBooking.
Matches existing Spring Boot entities exactly.
"""

from django.db import models
from accounts.models import User, Village


class Equipment(models.Model):
    """Equipment entity — matches existing Equipment.java exactly."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_equipment'
    )
    village = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name='equipment'
    )
    photo_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipments'

    def __str__(self):
        return self.name


class EquipmentBookingStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class EquipmentBooking(models.Model):
    """EquipmentBooking entity — matches existing EquipmentBooking.java exactly."""
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name='bookings'
    )
    renter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='equipment_bookings'
    )
    rental_hours = models.IntegerField()
    rental_minutes = models.IntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=EquipmentBookingStatus.choices,
        default=EquipmentBookingStatus.ACTIVE
    )
    available_again_at = models.DateTimeField(blank=True, null=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'equipment_bookings'
        ordering = ['-booked_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.equipment.name}"
