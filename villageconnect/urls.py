"""Main URL configuration for VillageConnect — wires all app URLs together."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


# ─── Frontend Template Views ──────────────────────────────────────

def index_view(request):
    return render(request, 'accounts/login.html')

def login_view(request):
    return render(request, 'accounts/login.html')

def register_view(request):
    return render(request, 'accounts/register.html')

def forgot_password_view(request):
    return render(request, 'accounts/forgot_password.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def announcements_view(request):
    return render(request, 'announcements/list.html')

def grievances_view(request):
    return render(request, 'grievances/list.html')

def grievance_create_view(request):
    return render(request, 'grievances/create.html')

def equipment_view(request):
    return render(request, 'agritech/equipment.html')

def mandi_prices_view(request):
    return render(request, 'agritech/mandi_prices.html')

def budget_view(request):
    return render(request, 'finance/budget.html')

def projects_view(request):
    return render(request, 'finance/projects.html')

def notifications_view(request):
    return render(request, 'notifications/list.html')


# ─── URL Patterns ─────────────────────────────────────────────────

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # ─── REST API Endpoints ────────────────────────────────────────
    path('api/auth/', include('accounts.urls')),
    path('api/villages/', include('villages.urls')),
    path('api/announcements/', include('announcements.urls')),
    path('api/grievances/', include('grievances.urls')),
    path('api/agritech/', include('agritech.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/notifications/', include('notifications.urls')),

    # ─── Frontend Pages (Bootstrap Templates) ──────────────────────
    path('', index_view, name='index'),
    path('login/', login_view, name='login-page'),
    path('register/', register_view, name='register-page'),
    path('forgot-password/', forgot_password_view, name='forgot-password-page'),
    path('dashboard/', dashboard_view, name='dashboard-page'),
    path('announcements/', announcements_view, name='announcements-page'),
    path('grievances/', grievances_view, name='grievances-page'),
    path('grievances/new/', grievance_create_view, name='grievance-create-page'),
    path('equipment/', equipment_view, name='equipment-page'),
    path('mandi-prices/', mandi_prices_view, name='mandi-prices-page'),
    path('budget/', budget_view, name='budget-page'),
    path('projects/', projects_view, name='projects-page'),
    path('notifications/', notifications_view, name='notifications-page'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
