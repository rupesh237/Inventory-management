from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import (
    CreateView, UpdateView, ListView, View
)
from django.contrib.messages.views import SuccessMessageMixin

from  django.conf import settings
import os
import logging
logger = logging.getLogger(__name__)

from weasyprint import HTML, CSS
from django.template.loader import get_template

from transactions.models import SaleBill, PurchaseBill, SaleBillDetails, PurchaseBillDetails
from inventory.models import Stock

from .models import Receipt, Payment, Report

import datetime
from django.utils import timezone


# Create your views here.
class ReportHomeView(View):
    template_name = "report/report_home.html"
    def get(self, request): 
        purchase_data = []
        sale_data = []
        today = timezone.now()
        a_months_ago = today - datetime.timedelta(days=30*1)

        # Data for purchase-graph
        purchase_bills = PurchaseBill.objects.filter(time__gte=a_months_ago, time__lte=today)
        for bill in purchase_bills:
            purchase_details = PurchaseBillDetails.objects.filter(billno=bill.billno)
            for item in purchase_details:
                supplier_name = bill.supplier.name
                found = False
                for purchase in purchase_data:
                    if supplier_name == purchase['supplier_name']:
                        purchase['total'] += item.total
                        purchase['paid'] += item.paid_amount
                        purchase['due'] += item.due_amount
                        found = True
                if not found:
                    purchase_data.append({
                        'supplier_name': bill.supplier.name,
                        'total': item.total,
                        'paid': item.paid_amount,
                        'due': item.due_amount,
                    })

        # Data for sales-graph
        sale_bills = SaleBill.objects.filter(time__gte=a_months_ago, time__lte=today)
        for bill in sale_bills:
            sale_details = SaleBillDetails.objects.filter(billno=bill.billno)
            for item in sale_details:
                customer_name = bill.name
                found = False
                for sale in sale_data:
                    if customer_name == sale['customer_name']:
                        sale['total'] += item.total
                        sale['paid'] += item.paid_amount
                        sale['due'] += item.due_amount
                        found = True
                if not found:
                    sale_data.append({
                        'customer_name': bill.name,
                        'total': item.total,
                        'paid': item.paid_amount,
                        'due': item.due_amount,
                    })

        context = {
            'purchase_data': purchase_data,
            'sale_data': sale_data,
        }
        return render(request, self.template_name, context)
    

# def general_ledger_function():
#     ledgers_list = Receipt.objects.all().values("date").distinct().order_by("-date").annotate(
#         sum_sharecapital_amount=Sum('sharecapital_amount'),
#         sum_entrancefee_amount=Sum('entrancefee_amount'),
#         sum_membershipfee_amount=Sum('membershipfee_amount'),
#         sum_bookfee_amount=Sum('bookfee_amount'),
#         sum_loanprocessingfee_amount=Sum('loanprocessingfee_amount'),
#         sum_savingsdeposit_thrift_amount=Sum('savingsdeposit_thrift_amount'),
#         sum_fixeddeposit_amount=Sum('fixeddeposit_amount'),
#         sum_recurringdeposit_amount=Sum('recurringdeposit_amount'),
#         sum_loanprinciple_amount=Sum('loanprinciple_amount'),
#         sum_loaninterest_amount=Sum('loaninterest_amount'),
#         sum_insurance_amount=Sum('insurance_amount'),
#         total_sum=Sum('sharecapital_amount') +
#                   Sum('entrancefee_amount') +
#                   Sum('membershipfee_amount') +
#                   Sum('bookfee_amount') +
#                   Sum('loanprocessingfee_amount') +
#                   Sum('savingsdeposit_thrift_amount') +
#                   Sum('fixeddeposit_amount') +
#                   Sum('recurringdeposit_amount') +
#                   Sum('loanprinciple_amount') +
#                   Sum('loaninterest_amount') +
#                   Sum('insurance_amount')
#     )
#     return ledgers_list

# def general_ledger(request):
#     ledgers_list = general_ledger_function()
#     return render(request, "generalledger.html", {'ledgers_list': ledgers_list})

# def general_ledger_pdf_download(request):
#     general_ledger_list = general_ledger_function()
#     try:
#         html_template = get_template("pdfgeneral_ledger.html")
#         context = {
#             'pagesize': 'A4',
#             "list": general_ledger_list,
#             "mediaroot": settings.MEDIA_ROOT
#         }
#         rendered_html = html_template.render(context).encode(encoding="UTF-8")
#         css_files = [
#             CSS(os.path.join(settings.STATIC_ROOT, 'css', 'mf.css')),
#             CSS(os.path.join(settings.STATIC_ROOT, 'css', 'pdf_stylesheet.css'))
#         ]
#         pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=css_files)
#         response = HttpResponse(pdf_file, content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="General_Ledger.pdf"'
#         return response
#     except Exception as err:
#         return HttpResponse(f'Error generating PDF: {err}', status=500)


# MIS Report pdf download
def mis_report_function(request, date):
    selected_date = timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))
    a_months_ago = selected_date - datetime.timedelta(days=30)
    receipts_list = []

    receipts_list = Receipt.objects.filter(date__gte=a_months_ago, date__lte=selected_date)
    receipt_types = [
        "SALE", "SERVICE PROVIDED", "DUE", "OTHER", 
    ]
    dict_receipts = {receipt_type: list(receipts_list.filter(type=receipt_type)) for receipt_type in receipt_types}
    dict_receipt_totals = {f"total_{key}": sum([r.total for r in value]) for key, value in dict_receipts.items()}
    dict_receipt_dues = {f"total_{key}_due": sum([r.due_amount for r in value]) for key, value in dict_receipts.items()}
    combined_totals = {**dict_receipt_totals, **dict_receipt_dues} 
    # Accessing specific totals
    service_provided_total = dict_receipt_totals.get('total_SERVICE PROVIDED', 0)
    service_provided_due = dict_receipt_dues.get('total_SERVICE PROVIDED_due', 0)

    total_sum_receipt = sum(dict_receipt_totals.values())
    total_due_receipt = sum(dict_receipt_dues.values())


    payments_list = Payment.objects.filter(date__gte=a_months_ago, date__lte=selected_date)
    payment_types = [
        "SALARY", "PURCHASE", "EXPENSE", "FOOD", 
        "TRAVEL", "DUE", "OTHER", 
    ]
    dict_payments = {payment_type: list(payments_list.filter(type=payment_type)) for payment_type in payment_types}
    dict_payments_totals = {key: sum([p.total for p in value]) for key, value in dict_payments.items()}
    dict_payments_dues = {key: sum([p.due_amount for p in value]) for key, value in dict_payments.items()}

    total_payments = sum(dict_payments_totals.values())
    due_payments = sum(dict_payments_dues.values())
    # print(dict_payments_totals)

    return {
        'receipts_list': list(receipts_list),
        'total_payments': total_payments,
        'due_payments': due_payments,
        'salary_list': dict_payments.get("SALARY", []),
        'purchase_list': dict_payments.get("PURCHASE", []),
        'expense_list': dict_payments.get("EXPENSE", []),
        'food_list': dict_payments.get("FOOD", []),
        'travel_list': dict_payments.get("TRAVEL", []),
        'payment_due_list': dict_payments.get("DUE", []),
        'other_payment_list': dict_payments.get("OTHER", []),
        'dict_payments': dict_payments_totals,
        'dict_payments_dues': dict_payments_dues,
        'selected_date': selected_date,
        'sale_list': dict_receipts.get("SALE", []),
        'service_provided_list': dict_receipts.get("SERVICE PROVIDED", []),
        'receipt_due_list': dict_receipts.get("DUE", []),
        'other_receipt_list': dict_receipts.get("OTHER", []),
        'service_provided_total': service_provided_total,
        'service_provided_due': service_provided_due,
        'total_sum_receipt': total_sum_receipt,
        'total_due_receipt': total_due_receipt,
        'dict_receipt_totals': dict_receipt_totals,
        'dict_receipt_dues': dict_receipt_dues,
    }


def mis_report(request):
    if request.method == 'POST':
        date_str = request.POST.get("date")
        try:
            date = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
        except (ValueError, TypeError):
            return render(request, "report/mis_report.html", {"error_message": "Invalid date format. Use MM/DD/YYYY."})
    else:
        date_str = request.GET.get("date")
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.datetime.now().date()
        except (ValueError, TypeError):
            return render(request, "report/mis_report.html", {"error_message": "Invalid date format. Use YYYY-MM-DD."})

    context = mis_report_function(request, date)
    context['date_formated'] = date.strftime("%m/%d/%Y")
    return render(request, "report/mis_report.html", context)




def mis_report_pdf_download(request, date):
    # Ensure 'date' is correctly retrieved
    date = request.GET.get("date") or date
    try:
        date_obj = datetime.datetime.strptime(date, '%m/%d/%Y').date()
    except ValueError:
        return HttpResponseBadRequest("Invalid date format. Please use MM/DD/YYYY.")

    report_data = mis_report_function(request, date_obj)
    
    try:
        context = {
            'pagesize': 'A4',
            "mediaroot": settings.MEDIA_ROOT,
            "receipts_list": report_data['receipts_list'],
            "total_payments": report_data['total_payments'],
            "due_payments": report_data['due_payments'],
            "purchase_list": report_data['purchase_list'],
            "salary_list": report_data['salary_list'],
            "expense_list": report_data['expense_list'],
            'food_list': report_data['food_list'],
            'travel_list': report_data['travel_list'],
            'payment_due_list': report_data['payment_due_list'],
            'other_payment_list': report_data['other_payment_list'],
            "dict_payments": report_data['dict_payments'],
            "dict_payments_dues": report_data['dict_payments_dues'],
            "selected_date": report_data['selected_date'],
            'sale_list': report_data['sale_list'],
            'service_provided_list': report_data['service_provided_list'],
            'receipt_due_list': report_data['receipt_due_list'],
            'other_receipt_list': report_data['other_receipt_list'],
            'service_provided_total': report_data['service_provided_total'],
            'service_provided_due': report_data['service_provided_due'],
            'total_sum_receipt': report_data['total_sum_receipt'],
            'total_due_receipt': report_data['total_due_receipt'],
            'dict_receipt_totals': report_data['dict_receipt_totals'],
            'dict_receipt_dues': report_data['dict_receipt_dues'],
        }

        html_template = get_template("report/pdf_mis_report.html")
        rendered_html = html_template.render(context).encode(encoding="UTF-8")
        css_files = [
            CSS(os.path.join(settings.STATIC_ROOT, 'css', 'mf.css')),
            CSS(os.path.join(settings.STATIC_ROOT, 'css', 'pdf_stylesheet.css'))
        ]

        # Debug statements to check paths
        logger.debug(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
        logger.debug(f'STATIC_ROOT: {settings.STATIC_ROOT}')
        logger.debug(f'Path to mf.css: {os.path.join(settings.STATIC_ROOT, "css", "mf.css")}')
        logger.debug(f'Path to pdf_stylesheet.css: {os.path.join(settings.STATIC_ROOT, "css", "pdf_stylesheet.css")}')

        pdf_file = HTML(string=rendered_html).write_pdf(stylesheets=css_files)

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mis-report.pdf"'

        return response

    except Exception as err:
        return HttpResponse(f'Error generating PDF: {err}', status=500)
