from django.urls import path
from finance import views

urlpatterns = [
    # Budget
    path('budget', views.create_or_update_budget, name='budget-create'),
    path('budget/', views.create_or_update_budget, name='budget-create-slash'),
    path('budget/village/<int:village_id>', views.get_budget, name='budget-get'),
    path('budget/village/<int:village_id>/', views.get_budget, name='budget-get-slash'),

    # Projects
    path('projects', views.create_project, name='project-create'),
    path('projects/', views.create_project, name='project-create-slash'),
    path('projects/village/<int:village_id>', views.village_projects, name='project-list'),
    path('projects/village/<int:village_id>/', views.village_projects, name='project-list-slash'),
    path('projects/<int:pk>/status', views.update_project_status, name='project-status'),
    path('projects/<int:pk>/status/', views.update_project_status, name='project-status-slash'),
]
