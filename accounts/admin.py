from django.contrib import admin
from accounts.models import User, Village


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'email', 'role', 'village', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'village']
    search_fields = ['name', 'phone', 'email']


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'block', 'district', 'state', 'pincode']
    search_fields = ['name', 'district', 'state']
