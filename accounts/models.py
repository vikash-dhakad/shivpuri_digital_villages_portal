"""User and Village models — matching existing Spring Boot entities exactly."""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserRole(models.TextChoices):
    VILLAGER = 'VILLAGER', 'Villager'
    FARMER = 'FARMER', 'Farmer'
    PANCHAYAT_ADMIN = 'PANCHAYAT_ADMIN', 'Panchayat Admin'


class Village(models.Model):
    """Village entity — matches existing Village.java exactly."""
    name = models.CharField(max_length=150)
    block = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'villages'

    def __str__(self):
        return f"{self.name}, {self.district}"


class UserManager(BaseUserManager):
    """Custom user manager using phone as the unique identifier."""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.PANCHAYAT_ADMIN)
        extra_fields.setdefault('name', 'Admin')
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User entity — matches existing User.java exactly.
    Uses phone as the unique identifier (USERNAME_FIELD), same as Spring Boot.
    """
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=150, unique=True, blank=True, null=True)
    role = models.CharField(max_length=30, choices=UserRole.choices, default=UserRole.VILLAGER)
    village = models.ForeignKey(
        Village, on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.phone})"
