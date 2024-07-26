from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    CreateView, UpdateView, ListView, View
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.utils import timezone

from .models import Receipt, Report, Payment

from .forms import ReceiptForm, PaymentForm

# Create your views here.
class ReceiptListView(ListView):
    model = Receipt
    template_name = "receipt/receipt_list.html"
    queryset = Receipt.objects.all()
    paginate_by = 10


class ReceiptCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Receipt                                                                       # setting 'Stock' model as model
    form_class = ReceiptForm                                                              # setting 'StockForm' form as form
    template_name = "receipt/add_receipt.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/report/receipt'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Receipt has been created successfully."                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Receipt'
        context["savebtn"] = 'Add Receipt'
        return context   
    
    def form_valid(self, form):
        form.instance.prepared_by = self.request.user

        # Set the date field to the current time if not provided
        if not form.cleaned_data.get('date'):
            form.instance.date = timezone.now()

        return super().form_valid(form)

    def form_invalid(self, form):
        # Print form errors to the console for debugging
        print(form.errors)
        return super().form_invalid(form)

class ReceiptDeleteView(View):                                                            # view class to delete stock
    template_name = "receipt/delete_receipt.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Receipt has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        receipt = get_object_or_404(Receipt, pk=pk)
        return render(request, self.template_name, {'object' : receipt})

    def post(self, request, pk):  
        receipt = get_object_or_404(Receipt, pk=pk)
        receipt.delete()                                             
        messages.success(request, self.success_message)
        return redirect('receipt') 

class PaymentListView(ListView):
    model = Payment
    template_name = "payment/payment_list.html"
    queryset = Payment.objects.all()
    paginate_by = 10


class PaymentCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Payment                                                                       # setting 'Stock' model as model
    form_class = PaymentForm                                                              # setting 'StockForm' form as form
    template_name = "payment/add_payment.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/report/payment'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Payment has been created successfully."                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Payment'
        context["savebtn"] = 'Add Payment'
        return context   
    
    def form_valid(self, form):
        # create report details object
        reportobj = Report()
        reportobj.save()
        form.instance.report = reportobj
        form.instance.prepared_by = self.request.user

        # Set the date field to the current time if not provided
        if not form.cleaned_data.get('date'):
            form.instance.date = timezone.now()

        return super().form_valid(form)

    def form_invalid(self, form):
        # Print form errors to the console for debugging
        print(form.errors)
        return super().form_invalid(form)
    
class PaymentDeleteView(View):                                                            # view class to delete stock
    template_name = "payment/delete_payment.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Payment has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        return render(request, self.template_name, {'object' : payment})

    def post(self, request, pk):  
        payment = get_object_or_404(Payment, pk=pk)
        payment.delete()                                             
        messages.success(request, self.success_message)
        return redirect('payment') 


