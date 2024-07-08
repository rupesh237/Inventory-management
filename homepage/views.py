from django.shortcuts import render
from django.views.generic import View, TemplateView
from inventory.models import Stock
from transactions.models import SaleBill, PurchaseBill, SaleItem, PurchaseItem
import datetime
from django.utils import timezone


class HomeView(View):
    template_name = "home.html"
    def get(self, request): 
        labels = []
        data = []
        purchase_data = []
        sale_data = []
        today = timezone.now()
        six_months_ago = today - datetime.timedelta(days=30*6)

        # Data for purchase-graph
        purchase_bills = PurchaseBill.objects.filter(time__gte=six_months_ago, time__lte=today)
        for bill in purchase_bills:
            purchase_items = PurchaseItem.objects.filter(billno=bill.billno)
            for item in purchase_items:
                stock_name = item.stock.name
                found = False
                for purchase in purchase_data:
                    if stock_name == purchase['name']:
                        purchase['quantity'] += item.quantity
                        purchase['totalprice'] += item.totalprice
                        found = True
                if not found:
                    purchase_data.append({
                        'name': item.stock.name,
                        'quantity': item.quantity,
                        'totalprice': item.totalprice
                    })

        # Data for sales-graph
        sale_bills = SaleBill.objects.filter(time__gte=six_months_ago, time__lte=today)
        for bill in sale_bills:
            sale_items = SaleItem.objects.filter(billno=bill.billno)
            for item in sale_items:
                stock_name = item.stock.name
                found = False
                for sale in sale_data:
                    if stock_name == sale['name']:
                        sale['quantity'] += item.quantity
                        sale['totalprice'] += item.totalprice
                        found = True
                if not found:
                    sale_data.append({
                        'name': item.stock.name,
                        'quantity': item.quantity,
                        'totalprice': item.totalprice
                    })
        
        stockqueryset = Stock.objects.filter(is_deleted=False).order_by('-quantity')
        for item in stockqueryset:
            labels.append(item.name)
            data.append(item.quantity)
        sales = SaleBill.objects.order_by('-time')[:3]
        purchases = PurchaseBill.objects.order_by('-time')[:3]
        context = {
            'labels'    : labels,
            'data'      : data,
            'purchase_data': purchase_data,
            'sale_data': sale_data,
            'sales'     : sales,
            'purchases' : purchases
        }
        return render(request, self.template_name, context)

class AboutView(TemplateView):
    template_name = "about.html"