from django.urls import path
from villages import views

urlpatterns = [
    path('', views.village_list_create, name='village-list-create'),
]
