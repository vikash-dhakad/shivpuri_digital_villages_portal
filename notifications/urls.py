from django.urls import path
from notifications import views

urlpatterns = [
    path('', views.get_my_notifications, name='notification-list'),
    path('unread-count', views.get_unread_count, name='notification-unread'),
    path('<int:pk>/read', views.mark_as_read, name='notification-read'),
    path('read-all', views.mark_all_as_read, name='notification-read-all'),
    path('<int:pk>', views.delete_notification, name='notification-delete'),
    path('clear', views.clear_all, name='notification-clear'),
]
