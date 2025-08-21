# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Task 1
    path('departments/create/', views.DepartmentCreateAPIView.as_view(), name='create-department'),
    # Task 2
    path('employees/create/', views.EmployeeCreateAPIView.as_view(), name='create-employee'),
    # Task 3
    path('employees/set-salary/', views.SetBaseSalaryAPIView.as_view(), name='set-base-salary'),
    # Task 4
    path('leaves/update/', views.UpdateLeaveCountAPIView.as_view(), name='update-leave-count'),
    # Task 5
    path('salary/calculate/', views.CalculatePayableSalaryAPIView.as_view(), name='calculate-salary'),
    # Task 6
    path('departments/<uuid:department_id>/high-earners/', views.HighEarnersInDepartmentAPIView.as_view(), name='high-earners-department'),
    # Task 7
    path('high-earners/month/', views.HighEarnersByMonthAPIView.as_view(), name='high-earners-month'),
]