from django.urls import path
from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='inventory'),
    path('new', views.StockCreateView.as_view(), name='new-stock'),
    path('stock/<pk>/edit', views.StockUpdateView.as_view(), name='edit-stock'),
    path('stock/<pk>/delete', views.StockDeleteView.as_view(), name='delete-stock'),

    path('stock/transfer/', views.StockTransferView.as_view(), name='transfer-stock'),
    path('stock-transfers/', views.StockTransferListView.as_view(), name='stock-transfer-list'),
    path('update-transfer-status/<int:transfer_id>/<str:action>/', views.update_transfer_status, name='update-transfer-status'),
]