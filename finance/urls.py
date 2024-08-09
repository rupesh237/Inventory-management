from django.urls import path
from .views import (
    EmployeeListView, EmployeeCreateView, EmployeeUpdateView, EmployeeDeleteView,
    PayrollCreateView, PayrollListView, PayrollUpdateView, PayrollDeleteView, 
    ReceiptListView, ReceiptCreateView, ReceiptUpdateView, ReceiptDeleteView, ReceiptBillView,
    PaymentListView, PaymentCreateView, PaymentUpdateView, PaymentDeleteView,
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

    path('receipt', ReceiptListView.as_view(), name="receipt"),
    path('receipt/new', ReceiptCreateView.as_view(), name='new-receipt'),
    path("receipt/<pk>/edit/", ReceiptUpdateView.as_view(), name="edit-receipt"),
    path("receipt/<pk>/delete/", ReceiptDeleteView.as_view(), name="delete-receipt"),
    path("receipt/bill/<receipt_no>", ReceiptBillView.as_view(), name="receipt-bill"),

    path('payment', PaymentListView.as_view(), name="payment"),
    path('payment/new', PaymentCreateView.as_view(), name='new-payment'),
    path("payment/<pk>/edit/", PaymentUpdateView.as_view(), name="edit-payment"),
    path("payment/<pk>/delete/", PaymentDeleteView.as_view(), name="delete-payment"),
]
