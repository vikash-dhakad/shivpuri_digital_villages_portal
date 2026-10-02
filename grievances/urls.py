from django.urls import path
from grievances import views

urlpatterns = [
    path('', views.create_grievance, name='grievance-create'),
    path('my', views.my_grievances, name='grievance-my'),
    path('village/<int:village_id>', views.village_grievances, name='grievance-village'),
    path('<int:pk>/status', views.update_status, name='grievance-status'),
    path('<int:pk>/reopen', views.reopen_grievance, name='grievance-reopen'),
    # Feedback routes
    path('feedbacks', views.list_feedbacks, name='grievance-feedbacks'),
    path('feedbacks/', views.list_feedbacks, name='grievance-feedbacks-slash'),
    path('<int:pk>/feedback', views.submit_feedback, name='grievance-feedback-submit'),
    path('<int:pk>/feedback/', views.submit_feedback, name='grievance-feedback-submit-slash'),
]
