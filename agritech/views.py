"""AgriTech views — matches AgriTechController.java + AgriTechService.java exactly.
Equipment CRUD, Booking, Mandi Prices.
"""

import os
import uuid
import logging
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agritech.models import Equipment, EquipmentBooking, EquipmentBookingStatus
from agritech.serializers import EquipmentSerializer, EquipmentBookingSerializer
from accounts.models import UserRole
from accounts.permissions import IsFarmer, IsVillagerFarmerOrAdmin
from finance.models import Budget
from notifications.models import NotificationType
from notifications.services import send_notification

logger = logging.getLogger(__name__)


def _save_uploaded_file(file, subfolder):
    """Save uploaded file and return URL path."""
    if file is None:
        return None
    upload_dir = os.path.join(settings.MEDIA_ROOT, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.name)[1] if file.name else ''
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return f"{settings.MEDIA_URL}{subfolder}/{filename}"


from rest_framework.permissions import AllowAny

# ─── Mandi Prices & Locations ──────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def get_mandi_locations(request):
    """GET /api/agritech/mandi-locations/ — returns available States and Districts for dropdowns."""
    from agritech.tasks import get_available_locations
    return Response(get_available_locations())


@api_view(['GET'])
@permission_classes([AllowAny])
def get_mandi_prices(request):
    """GET /api/agritech/mandi-prices/ — returns Mandi prices filtered by state, district, and optional crop."""
    state = request.GET.get('state', '').strip()
    district = request.GET.get('district', '').strip()
    crop = request.GET.get('crop', '').strip()

    cache_key = f"mandi_prices_{state or 'all'}_{district or 'all'}"
    cache_key = cache_key.replace(' ', '_').lower()

    if not crop:
        try:
            cached_prices = cache.get(cache_key)
            if cached_prices:
                return Response(cached_prices)
        except Exception:
            pass

    from agritech.tasks import fetch_mandi_prices
    prices = fetch_mandi_prices(state=state, district=district, crop=crop)
    return Response(prices or [])


# ─── Equipment CRUD ────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsVillagerFarmerOrAdmin])
def add_equipment(request):
    """POST /api/agritech/equipments/ — matches AgriTechService.addEquipment()."""
    user = request.user
    photo = request.FILES.get('photo')
    photo_url = _save_uploaded_file(photo, 'equipment-photos')

    equipment = Equipment.objects.create(
        owner=user,
        village=user.village,
        name=request.data.get('name', ''),
        description=request.data.get('description', ''),
        price_per_hour=Decimal(request.data.get('pricePerHour', '0')),
        photo_url=photo_url,
    )
    serializer = EquipmentSerializer(equipment)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsVillagerFarmerOrAdmin])
def available_equipments(request, village_id):
    """GET /api/agritech/equipments/village/<id>/ — available only."""
    vid = village_id if (village_id and village_id > 0) else (request.user.village_id if request.user.village else None)
    if vid:
        equipments = Equipment.objects.filter(village_id=vid, available=True).select_related('owner', 'village')
    else:
        equipments = Equipment.objects.filter(available=True).select_related('owner', 'village')
    serializer = EquipmentSerializer(equipments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsVillagerFarmerOrAdmin])
def all_equipments(request, village_id):
    """GET /api/agritech/equipments/village/<id>/all/ — all including unavailable."""
    vid = village_id if (village_id and village_id > 0) else (request.user.village_id if request.user.village else None)
    if vid:
        equipments = Equipment.objects.filter(village_id=vid).select_related('owner', 'village')
    else:
        equipments = Equipment.objects.all().select_related('owner', 'village')
    serializer = EquipmentSerializer(equipments, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsVillagerFarmerOrAdmin])
def toggle_availability(request, pk):
    """PUT /api/agritech/equipments/<id>/toggle-availability/ — owner only."""
    try:
        equipment = Equipment.objects.select_related('owner', 'village').get(id=pk)
    except Equipment.DoesNotExist:
        return Response({'error': 'Equipment not found'}, status=status.HTTP_404_NOT_FOUND)

    if equipment.owner.phone != request.user.phone:
        return Response(
            {'error': 'Only owner can change availability'},
            status=status.HTTP_403_FORBIDDEN
        )

    equipment.available = not equipment.available
    equipment.save(update_fields=['available'])
    serializer = EquipmentSerializer(equipment)
    return Response(serializer.data)


# ─── Equipment Booking ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsVillagerFarmerOrAdmin])
@transaction.atomic
def book_equipment(request, pk):
    """POST /api/agritech/equipments/<id>/book/ — matches AgriTechService.bookEquipment() exactly."""
    renter = request.user

    try:
        equipment = Equipment.objects.select_related('owner', 'village').get(id=pk)
    except Equipment.DoesNotExist:
        return Response({'error': 'Equipment not found'}, status=status.HTTP_404_NOT_FOUND)

    if not equipment.available:
        return Response(
            {'error': 'Equipment is currently not available for booking.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if equipment.owner_id == renter.id or (equipment.owner and equipment.owner.phone == renter.phone):
        return Response(
            {'error': 'Aap apna khud ka equipment book nahi kar sakte (You cannot book your own equipment).'},
            status=status.HTTP_400_BAD_REQUEST
        )

    hours = int(request.data.get('hours', 0))
    minutes = int(request.data.get('minutes', 0))

    # Calculate total cost (exact same formula as Java)
    hourly_cost = equipment.price_per_hour * Decimal(hours)
    min_cost = (equipment.price_per_hour * Decimal(minutes) / Decimal(60)).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    total_cost = hourly_cost + min_cost

    # Calculate when equipment becomes available again (rental time + 30 min buffer)
    now = timezone.now()
    available_again_at = now + timedelta(hours=hours, minutes=minutes + 30)

    booking = EquipmentBooking.objects.create(
        equipment=equipment,
        renter=renter,
        rental_hours=hours,
        rental_minutes=minutes,
        total_cost=total_cost,
        status=EquipmentBookingStatus.ACTIVE,
        available_again_at=available_again_at,
    )

    # Mark equipment as unavailable
    equipment.available = False
    equipment.save(update_fields=['available'])

    # If equipment is owned by Panchayat Admin, directly add rent value to Panchayat Budget
    if equipment.owner and equipment.owner.role == UserRole.PANCHAYAT_ADMIN:
        village = equipment.village or equipment.owner.village
        if village:
            budget = Budget.objects.filter(village=village).order_by('-id').first()
            if not budget:
                budget = Budget.objects.create(
                    village=village,
                    fiscal_year='2024-2025',
                    total_amount=total_cost,
                )
            else:
                budget.total_amount += total_cost
                budget.save(update_fields=['total_amount', 'updated_at'])

            send_notification(
                equipment.owner_id,
                'Budget me Rent Add Hua!',
                f'{equipment.name} ka rent ₹{total_cost} seedhe Panchayat Budget me add ho gaya hai.',
                NotificationType.FINANCE,
                booking.id,
            )

    # Send persistent notification to owner
    send_notification(
        equipment.owner_id,
        'Equipment Booked!',
        f'Your {equipment.name} has been booked by {renter.name} for {hours}h {minutes}m. '
        f'Rent: \u20b9{total_cost}. Contact: {renter.phone}',
        NotificationType.BOOKING,
        booking.id,
    )

    # Send persistent notification to renter
    send_notification(
        renter.id,
        'Booking Confirmed!',
        f'You booked {equipment.name} for {hours}h {minutes}m. Total: \u20b9{total_cost}. '
        f'Owner: {equipment.owner.name} ({equipment.owner.phone})',
        NotificationType.BOOKING,
        booking.id,
    )

    serializer = EquipmentBookingSerializer(booking)
    return Response(serializer.data)


# ─── Booking History ───────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsVillagerFarmerOrAdmin])
def my_bookings(request):
    """GET /api/agritech/bookings/my/ — renter's booking history."""
    bookings = EquipmentBooking.objects.filter(renter=request.user).select_related(
        'equipment', 'equipment__owner', 'renter'
    )
    serializer = EquipmentBookingSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsVillagerFarmerOrAdmin])
def owner_booking_log(request):
    """GET /api/agritech/bookings/owner/ — owner's equipment booking log."""
    bookings = EquipmentBooking.objects.filter(
        equipment__owner=request.user
    ).select_related('equipment', 'equipment__owner', 'renter')
    serializer = EquipmentBookingSerializer(bookings, many=True)
    return Response(serializer.data)
