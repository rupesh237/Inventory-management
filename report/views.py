from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    CreateView, UpdateView, ListView, View
)
from django.contrib.messages.views import SuccessMessageMixin

from transactions.models import SaleBill, PurchaseBill, SaleBillDetails, PurchaseBillDetails
from inventory.models import Stock

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