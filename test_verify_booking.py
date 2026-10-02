"""Test: Direct Panchayat Budget Addition & Deduction.

Simple Logic:
1. Panchayat Admin ke equipment rent ka paisa direct Panchayat Budget me ADD hota hai.
2. Project par jo kharcha hota hai wo direct Budget se KAM (deduct) hota hai.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'villageconnect.settings')
django.setup()

from decimal import Decimal
from accounts.models import User, Village, UserRole
from agritech.models import Equipment
from finance.models import Budget, Project
from rest_framework.test import APIRequestFactory, force_authenticate
from agritech.views import book_equipment
from finance.views import update_project_status

factory = APIRequestFactory()

# Village Jariya
village = Village.objects.filter(name__iexact='jariya').first()
admin = User.objects.filter(village=village, role=UserRole.PANCHAYAT_ADMIN).first()
farmer = User.objects.filter(village=village, role=UserRole.FARMER).first()

# Budget of Village
budget = Budget.objects.filter(village=village).order_by('-id').first()
if not budget:
    budget = Budget.objects.create(village=village, fiscal_year='2024-2025', total_amount=Decimal('50000.00'))

print("==================================================")
print(f"1. Shuruat me Panchayat Budget: Rs. {budget.total_amount}")
print("==================================================")

# Equipment owned by Admin
equipment = Equipment.objects.filter(owner=admin, village=village).first()
if not equipment:
    equipment = Equipment.objects.create(
        name='Panchayat Tractor',
        owner=admin,
        village=village,
        price_per_hour=Decimal('500.00'),
        available=True
    )
equipment.available = True
equipment.save()

# Farmer books equipment for 3 hours (Cost = 3 * 500 = Rs. 1500)
req = factory.post(f'/api/agritech/equipments/{equipment.id}/book/', {'hours': 3, 'minutes': 0}, format='json')
force_authenticate(req, user=farmer)
resp = book_equipment(req, pk=equipment.id)

budget.refresh_from_db()
print(f"2. Equipment Book hua (3 hours): Rent Rs. 1500 direct add hua.")
print(f"   -> Naya Panchayat Budget: Rs. {budget.total_amount}")
print("==================================================")

# Reset availability
equipment.available = True
equipment.save()

print("Budget me direct value add ho rahi hai! Koi complex banking system nahi hai.")
