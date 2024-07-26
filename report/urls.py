from django.urls import path
from .views import ReceiptCreateView, ReceiptListView, ReceiptDeleteView, PaymentCreateView, PaymentListView, PaymentDeleteView

urlpatterns = [
    path('receipt', ReceiptListView.as_view(), name="receipt"),
    path('receipt/new', ReceiptCreateView.as_view(), name='new-receipt'),
    path("receipt/<pk>/delete/", ReceiptDeleteView.as_view(), name="delete-receipt"),

    path('payment', PaymentListView.as_view(), name="payment"),
    path('payment/new', PaymentCreateView.as_view(), name='new-payment'),
    path("payment/<pk>/delete/", PaymentDeleteView.as_view(), name="delete-payment"),
]
