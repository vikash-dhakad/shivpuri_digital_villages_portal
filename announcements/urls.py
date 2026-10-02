from django.urls import path
from announcements import views

urlpatterns = [
    path('', views.create_announcement, name='announcement-create'),
    path('village/<int:village_id>', views.village_announcements, name='announcement-village'),
]
