"""AgriTech serializers matching existing DTOs."""

from rest_framework import serializers
from agritech.models import Equipment, EquipmentBooking


class EquipmentSerializer(serializers.ModelSerializer):
    """Matches EquipmentResponse.java."""
    pricePerHour = serializers.DecimalField(source='price_per_hour', max_digits=10, decimal_places=2)
    photoUrl = serializers.CharField(source='photo_url', allow_null=True)
    ownerId = serializers.IntegerField(source='owner.id', read_only=True)
    ownerName = serializers.CharField(source='owner.name', read_only=True)
    ownerRole = serializers.CharField(source='owner.role', read_only=True)
    ownerPhone = serializers.CharField(source='owner.phone', read_only=True)
    villageName = serializers.CharField(source='village.name', read_only=True)
    isPanchayat = serializers.SerializerMethodField()

    def get_isPanchayat(self, obj):
        return bool(obj.owner and obj.owner.role == 'PANCHAYAT_ADMIN')

    class Meta:
        model = Equipment
        fields = ['id', 'name', 'description', 'pricePerHour', 'available', 'photoUrl',
                  'ownerId', 'ownerName', 'ownerRole', 'ownerPhone', 'villageName', 'isPanchayat']


class EquipmentBookingSerializer(serializers.ModelSerializer):
    """Matches EquipmentBookingResponse.java."""
    bookingId = serializers.IntegerField(source='id', read_only=True)
    equipmentId = serializers.IntegerField(source='equipment_id', read_only=True)
    equipmentName = serializers.CharField(source='equipment.name', read_only=True)
    equipmentPhotoUrl = serializers.CharField(source='equipment.photo_url', read_only=True)
    rentalHours = serializers.IntegerField(source='rental_hours')
    rentalMinutes = serializers.IntegerField(source='rental_minutes')
    totalCost = serializers.DecimalField(source='total_cost', max_digits=10, decimal_places=2)
    bookedAt = serializers.DateTimeField(source='booked_at', read_only=True)
    availableAgainAt = serializers.DateTimeField(source='available_again_at', read_only=True)
    renterName = serializers.CharField(source='renter.name', read_only=True)
    renterPhone = serializers.CharField(source='renter.phone', read_only=True)
    ownerName = serializers.CharField(source='equipment.owner.name', read_only=True)
    ownerPhone = serializers.CharField(source='equipment.owner.phone', read_only=True)

    class Meta:
        model = EquipmentBooking
        fields = ['bookingId', 'equipmentId', 'equipmentName', 'equipmentPhotoUrl',
                  'rentalHours', 'rentalMinutes', 'totalCost', 'bookedAt', 'status',
                  'availableAgainAt', 'renterName', 'renterPhone', 'ownerName', 'ownerPhone']


class MandiPriceSerializer(serializers.Serializer):
    """Matches MandiPriceResponse.java."""
    commodity = serializers.CharField()
    state = serializers.CharField()
    market = serializers.CharField()
    minPrice = serializers.DecimalField(max_digits=10, decimal_places=2)
    maxPrice = serializers.DecimalField(max_digits=10, decimal_places=2)
    modalPrice = serializers.DecimalField(max_digits=10, decimal_places=2)
    lastUpdated = serializers.CharField()
