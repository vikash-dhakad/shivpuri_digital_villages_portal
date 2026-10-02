from django.urls import path
from agritech import views

urlpatterns = [
    # Mandi Prices & Locations
    path('mandi-prices', views.get_mandi_prices, name='mandi-prices'),
    path('mandi-prices/', views.get_mandi_prices, name='mandi-prices-slash'),
    path('mandi-locations', views.get_mandi_locations, name='mandi-locations'),
    path('mandi-locations/', views.get_mandi_locations, name='mandi-locations-slash'),

    # Equipment CRUD
    path('equipments', views.add_equipment, name='equipment-add'),
    path('equipments/', views.add_equipment, name='equipment-add-slash'),
    path('equipments/village/<int:village_id>', views.available_equipments, name='equipment-available'),
    path('equipments/village/<int:village_id>/', views.available_equipments, name='equipment-available-slash'),
    path('equipments/village/<int:village_id>/all', views.all_equipments, name='equipment-all'),
    path('equipments/village/<int:village_id>/all/', views.all_equipments, name='equipment-all-slash'),
    path('equipments/<int:pk>/toggle-availability', views.toggle_availability, name='equipment-toggle'),
    path('equipments/<int:pk>/toggle-availability/', views.toggle_availability, name='equipment-toggle-slash'),

    # Equipment Booking (support both with and without trailing slash)
    path('equipments/<int:pk>/book', views.book_equipment, name='equipment-book'),
    path('equipments/<int:pk>/book/', views.book_equipment, name='equipment-book-slash'),
    path('bookings/my', views.my_bookings, name='booking-my'),
    path('bookings/my/', views.my_bookings, name='booking-my-slash'),
    path('bookings/owner', views.owner_booking_log, name='booking-owner'),
    path('bookings/owner/', views.owner_booking_log, name='booking-owner-slash'),
]
