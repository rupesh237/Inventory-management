from django.urls import path

from .views import (
    ReportHomeView, 
    mis_report, mis_report_pdf_download, 
    day_book, day_book_pdf_download,
    receipt_report, receipt_report_pdf_download,
    payment_report, payment_report_pdf_download,)

urlpatterns = [
    path('home', ReportHomeView.as_view(), name='report-home'),
    path('mis_report', mis_report, name='mis-report'),
    path('mis_report_download/<path:date>', mis_report_pdf_download, name='mis-report-pdf'),

    path('day_book', day_book, name='day-book'),
    path('daybook_download/<path:date>', day_book_pdf_download, name='day-book-pdf'),

    path('receipt_report', receipt_report, name='receipt-report'),
    path('receipt_report_download/<path:date>', receipt_report_pdf_download, name='receipt-report-pdf'),

    path('payment_report', payment_report, name='payment-report'),
    path('payment_report_download/<path:date>', payment_report_pdf_download, name='payment-report-pdf'),
    
]
