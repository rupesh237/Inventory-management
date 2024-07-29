from django.urls import path

from .views import ReportHomeView

urlpatterns = [
    path('home', ReportHomeView.as_view(), name='report-home'),
    
]
