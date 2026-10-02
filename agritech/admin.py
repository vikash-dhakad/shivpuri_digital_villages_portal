from django.contrib import admin
from agritech.models import Equipment, EquipmentBooking

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price_per_hour', 'available', 'owner', 'village']
    list_filter = ['available', 'village']
    search_fields = ['name']

@admin.register(EquipmentBooking)
class EquipmentBookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'equipment', 'renter', 'rental_hours', 'rental_minutes', 'total_cost', 'status', 'booked_at']
    list_filter = ['status']
