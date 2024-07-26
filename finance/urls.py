from django.urls import path
from .views import (
    EmployeeListView,
    EmployeeCreateView,
    EmployeeUpdateView,
    EmployeeDeleteView,
    PayrollCreateView, PayrollListView, PayrollUpdateView, PayrollDeleteView
)

urlpatterns = [
    path("employee", EmployeeListView.as_view(), name="employee"),
    path("employee/new/", EmployeeCreateView.as_view(), name="new-employee"),
    path("employee/<pk>/edit/", EmployeeUpdateView.as_view(), name="edit-employee"),
    path("employee/<pk>/delete/", EmployeeDeleteView.as_view(), name="delete-employee"),

    path("payroll", PayrollListView.as_view(), name="payroll"),
    path("payroll/new", PayrollCreateView.as_view(), name='new-payroll'),
    path("payroll/<pk>/edit/", PayrollUpdateView.as_view(), name="edit-payroll"),
    path("payroll/<pk>/delete/", PayrollDeleteView.as_view(), name="delete-payroll"),
]
