from django.urls import path

from .views import ReportHomeView, mis_report, mis_report_pdf_download

urlpatterns = [
    path('home', ReportHomeView.as_view(), name='report-home'),
    path('mis_report', mis_report, name='mis-report'),
    path('misreport_pdfdownload/<path:date>', mis_report_pdf_download, name='misreport-pdfdownload'),
    
]
