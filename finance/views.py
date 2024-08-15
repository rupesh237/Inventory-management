from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    View,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.utils import timezone
import tzlocal
from django.urls import reverse

from django_filters.views import FilterView

from .models import Employee, Payroll
from .forms import EmployeeForm, PayrollForm, ReceiptForm, PaymentForm, ReceiptBillForm

from report.models import Receipt, ReceiptBill, Payment

from .filters import PayrollFilter

# Create your views here.
class EmployeeListView(ListView):
    model = Employee
    template_name = "employee/employee_list.html"
    paginate_by = 10

    def get_queryset(self):
        user_branch = self.request.user.profile.branch
        return Employee.objects.filter(branch=user_branch)


class EmployeeCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Employee                                                                       # setting 'Stock' model as model
    form_class = EmployeeForm                                                              # setting 'StockForm' form as form
    template_name = "employee/add_employee.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/finance/employee'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Employee has been created successfully."                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Employee'
        context["savebtn"] = 'Add Employee'
        return context

    def get_form_kwargs(self):
        """Pass the request object to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Add the request to the form kwargs
        return kwargs  
   
    
    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        # Print form errors to the console for debugging
        print(form.errors)
        return super().form_invalid(form)

class EmployeeUpdateView(SuccessMessageMixin, UpdateView):                                 
    model = Employee                                                                      
    form_class = EmployeeForm                                                             
    template_name = "employee/edit_employee.html"                                            
    success_url = '/finance/employee'                                                          
    success_message = "Employee's details has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Employee'
        context["savebtn"] = 'Update'
        context["delbtn"] = 'Delete'
        return context


class EmployeeDeleteView(View):                                                           
    template_name = "employee/delete_employee.html"                                                 
    success_message = "Employee has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        branch = self.request.user.profile.branch
        employee = get_object_or_404(Employee, pk=pk, branch=branch)
        return render(request, self.template_name, {'object' : employee})

    def post(self, request, pk):  
        branch = self.request.user.profile.branch
        employee = get_object_or_404(Employee, pk=pk, branch=branch)
        employee.delete()                                             
        messages.success(request, self.success_message)
        return redirect('employee') 
    
# used to view a supplier's profile
class EmployeeView(View):
    def get(self, request, pk):
        branch = self.request.user.profile.branch
        overall_total_amount = 0
        employeeobj = get_object_or_404(Employee, pk=pk, branch=branch)
        payroll_list = Payroll.objects.filter(employee=employeeobj)
        for payroll in payroll_list:
           # Calculate the total amount for each payroll
            overall_total_amount += payroll.net_salary
        page = request.GET.get('page', 1)
        paginator = Paginator(payroll_list, 10)
        try:
            payrolls = paginator.page(page)
        except PageNotAnInteger:
            payrolls = paginator.page(1)
        except EmptyPage:
            payrolls = paginator.page(paginator.num_pages)
        context = {
            'employee'  : employeeobj,
            'payrolls'     : payrolls,
            'overall_total_amount': overall_total_amount,
        }
        return render(request, 'employee/employee.html', context)


class PayrollCreateView(SuccessMessageMixin, CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'payroll/create_payroll.html'
    success_url = '/finance/payroll'  # Redirect after successful form submission
    success_message = "Payroll has been created successfully." 

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Pyroll'
        context["savebtn"] = 'Add Payroll'
        return context  
    
    def get_form_kwargs(self):
        """Pass the request object to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Add the request to the form kwargs
        return kwargs  

    def form_valid(self, form):
        form.instance.calculate_net_salary()          # Ensure net salary is calculated
        payroll = form.save(commit=False)
        payroll.prepared_by = self.request.user
        return super().form_valid(form)

class PayrollListView(FilterView):
    filterset_class = PayrollFilter
    template_name = 'payroll/payroll_list.html'
    paginate_by = 10

    def get_queryset(self):
        # Get the branch of the current user
        user_branch = self.request.user.profile.branch
        # Filter the Payroll objects by the user's branch
        queryset = Payroll.objects.filter(branch=user_branch)
        # Apply the filter class to the queryset
        filtered_queryset = self.filterset_class(self.request.GET, queryset=queryset).qs
        return filtered_queryset

class PayrollUpdateView(SuccessMessageMixin, UpdateView):                                 
    model = Payroll                                                                       
    form_class = PayrollForm                                                              
    template_name = "payroll/edit_payroll.html"                                                 
    success_url = '/finance/payroll'                   
    success_message = "Payroll details has been updated successfully."                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Payroll'
        context["savebtn"] = 'Update'
        context["delbtn"] = 'Delete'
        return context
    
    def get_form_kwargs(self):
        """Pass the request object to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Add the request to the form kwargs
        return kwargs  
    
    def form_valid(self, form):
        form.instance.calculate_net_salary()          # Ensure net salary is calculated
        payroll = form.save(commit=False)
        payroll.prepared_by = self.request.user
        return super().form_valid(form)


class PayrollDeleteView(View):                                                            # view class to delete stock
    template_name = "payroll/delete_payroll.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Payroll has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        branch = self.request.user.profile.branch
        payroll = get_object_or_404(Payroll, pk=pk, branch=branch)
        return render(request, self.template_name, {'object' : payroll})

    def post(self, request, pk):  
        branch = self.request.user.profile.branch
        payroll = get_object_or_404(Payroll, pk=pk, branch=branch)
        payroll.delete()                                             
        messages.success(request, self.success_message)
        return redirect('payroll') 
    
class ReceiptListView(ListView):
    model = Receipt
    template_name = "receipt/receipt_list.html"
    paginate_by = 10

    def get_queryset(self):
        user_branch = self.request.user.profile.branch
        return Receipt.objects.filter(branch=user_branch)


class ReceiptCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Receipt                                                                       # setting 'Stock' model as model
    form_class = ReceiptForm                                                              # setting 'StockForm' form as form
    template_name = "receipt/add_receipt.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/finance/receipt'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Receipt has been created successfully."                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Receipt'
        context["savebtn"] = 'Add Receipt'
        return context   
    
    def get_form_kwargs(self):
        """Pass the request object to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Add the request to the form kwargs
        return kwargs  
    
    def form_valid(self, form):
        form.instance.prepared_by = self.request.user

        # Set the date field to the current time if not provided
        if not form.cleaned_data.get('date'):
            local_tz = tzlocal.get_localzone()  # Get the system's local timezone
            print(local_tz)
            form.instance.date = timezone.now().astimezone(local_tz)
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirect to the ReceiptBillView for the newly created receipt
        return reverse('receipt-bill', kwargs={'receipt_no': self.object.receipt_no})

    def form_invalid(self, form):
        # Print form errors to the console for debugging
        print(form.errors)
        return super().form_invalid(form)
    
class ReceiptUpdateView(SuccessMessageMixin, UpdateView):                                 
    model = Receipt                                                                      
    form_class = ReceiptForm                                                             
    template_name = "receipt/edit_receipt.html"                                            
    success_url = '/finance/receipt'                                                        
    success_message = "Receipt has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Receipt'
        context["savebtn"] = 'Update'
        context["delbtn"] = 'Delete'
        return context
    
    def get_success_url(self):
        # Redirect to the ReceiptBillView for the newly created receipt
        return reverse('receipt-bill', kwargs={'receipt_no': self.object.receipt_no})

class ReceiptDeleteView(View):                                                            # view class to delete stock
    template_name = "receipt/delete_receipt.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Receipt has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        branch = self.request.user.profile.branch
        receipt = get_object_or_404(Receipt, pk=pk, branch=branch)
        return render(request, self.template_name, {'object' : receipt})

    def post(self, request, pk):  
        branch = self.request.user.profile.branch
        receipt = get_object_or_404(Receipt, pk=pk, branch=branch)
        receipt.delete()                                             
        messages.success(request, self.success_message)
        return redirect('receipt') 

class PaymentListView(ListView):
    model = Payment
    template_name = "payment/payment_list.html"
    paginate_by = 10

    def get_queryset(self):
        user_branch = self.request.user.profile.branch
        return Payment.objects.filter(branch=user_branch)


class PaymentCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Payment                                                                       # setting 'Stock' model as model
    form_class = PaymentForm                                                              # setting 'StockForm' form as form
    template_name = "payment/add_payment.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/finance/payment'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Payment has been created successfully."                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Payment'
        context["savebtn"] = 'Add Payment'
        return context   
    
    def get_form_kwargs(self):
        """Pass the request object to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Add the request to the form kwargs
        return kwargs  
    
    def form_valid(self, form):
        form.instance.prepared_by = self.request.user

        # Set the date field to the current time if not provided
        if not form.cleaned_data.get('date'):
            local_tz = tzlocal.get_localzone()  # Get the system's local timezone
            form.instance.date = timezone.now().astimezone(local_tz)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Print form errors to the console for debugging
        print(form.errors)
        return super().form_invalid(form)
    
class PaymentUpdateView(SuccessMessageMixin, UpdateView):                                 
    model = Payment                                                                      
    form_class = PaymentForm                                                             
    template_name = "payment/edit_payment.html"                                            
    success_url = '/finance/payment'                                                        
    success_message = "Payment has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Payment'
        context["savebtn"] = 'Update'
        context["delbtn"] = 'Delete'
        return context

    
class PaymentDeleteView(View):                                                            # view class to delete stock
    template_name = "payment/delete_payment.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Payment has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        branch = self.request.user.profile.branch
        payment = get_object_or_404(Payment, pk=pk, branch=branch)
        return render(request, self.template_name, {'object' : payment})

    def post(self, request, pk):  
        branch = self.request.user.profile.branch
        payment = get_object_or_404(Payment, pk=pk, branch=branch)
        payment.delete()                                             
        messages.success(request, self.success_message)
        return redirect('payment') 


# used to display the receipt bill object
class ReceiptBillView(View):
    model = ReceiptBill
    template_name = "receipt/bill/receipt_bill.html"
    bill_base = "receipt/bill/bill_base.html"
    
    def get(self, request, receipt_no):
        receipt = Receipt.objects.get(receipt_no=receipt_no)
        context = {
            'bill'          : ReceiptBill.objects.get(receipt=receipt),
            'bill_base'     : self.bill_base,
            # 'bill_total'    : (SaleBill.objects.get(billno=billno)).get_total_price()
        }
        return render(request, self.template_name, context)

    def post(self, request, receipt_no):
        form = ReceiptBillForm(request.POST)
        if form.is_valid():
            receipt = Receipt.objects.get(receipt_no=receipt_no)
            billdetailsobj = ReceiptBill.objects.get(receipt=receipt)
            
           # Update billdetailsobj with form data
            billdetailsobj.eway = form.cleaned_data.get('eway')
            billdetailsobj.veh = form.cleaned_data.get('veh')
            billdetailsobj.destination = form.cleaned_data.get('destination')
            billdetailsobj.po = form.cleaned_data.get('po')
            billdetailsobj.cgst = form.cleaned_data.get('cgst')
            billdetailsobj.sgst = form.cleaned_data.get('sgst')
            billdetailsobj.igst = form.cleaned_data.get('igst')
            billdetailsobj.cess = form.cleaned_data.get('cess')
            billdetailsobj.tcs = form.cleaned_data.get('tcs')
            billdetailsobj.discount_amount = form.cleaned_data.get('discount_amount')
            billdetailsobj.total = form.cleaned_data.get('total')
            billdetailsobj.paid_amount = form.cleaned_data.get('paid_amount', 0)
            billdetailsobj.due_amount = form.cleaned_data.get('due_amount', 0)

            if billdetailsobj.paid_amount is None:
                billdetailsobj.paid_amount = 0.0

            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        else:
             # Print form errors to debug
            print(form.errors)
            messages.error(request, "Form is Invaid.")
        context = {
            'bill'          : ReceiptBill.objects.get(receipt=receipt_no),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)



