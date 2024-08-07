from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    View,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.utils import timezone

from django_filters.views import FilterView

from .models import Employee, Payroll
from .forms import EmployeeForm, PayrollForm, ReceiptForm, PaymentForm

from report.models import Receipt, Report, Payment

from .filters import PayrollFilter

# Create your views here.
class EmployeeListView(ListView):
    model = Employee
    template_name = "employee/employee_list.html"
    queryset = Employee.objects.all()
    paginate_by = 10


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
        context["savebtn"] = 'Update Employee'
        context["delbtn"] = 'Delete Employee'
        return context


class EmployeeDeleteView(View):                                                           
    template_name = "employee/delete_employee.html"                                                 
    success_message = "Employee has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        return render(request, self.template_name, {'object' : employee})

    def post(self, request, pk):  
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()                                             
        messages.success(request, self.success_message)
        return redirect('employee') 


class PayrollCreateView(CreateView):
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

    def form_valid(self, form):
        form.instance.calculate_net_salary()          # Ensure net salary is calculated
        payroll = form.save(commit=False)
        payroll.prepared_by = self.request.user
        return super().form_valid(form)

class PayrollListView(FilterView):
    filterset_class = PayrollFilter
    queryset = Payroll.objects.filter()
    template_name = 'payroll/payroll_list.html'
    paginate_by = 10

class PayrollUpdateView(SuccessMessageMixin, UpdateView):                                 
    model = Payroll                                                                       
    form_class = PayrollForm                                                              
    template_name = "payroll/edit_payroll.html"                                                 
    success_url = '/finance/payroll'                   
    success_message = "Payroll details has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Payroll'
        context["savebtn"] = 'Update Payroll'
        context["delbtn"] = 'Delete Payroll'
        return context
    
    def form_valid(self, form):
        form.instance.calculate_net_salary()          # Ensure net salary is calculated
        payroll = form.save(commit=False)
        payroll.prepared_by = self.request.user
        return super().form_valid(form)


class PayrollDeleteView(View):                                                            # view class to delete stock
    template_name = "payroll/delete_payroll.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Payroll has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        return render(request, self.template_name, {'object' : payroll})

    def post(self, request, pk):  
        payroll = get_object_or_404(Payroll, pk=pk)
        payroll.delete()                                             
        messages.success(request, self.success_message)
        return redirect('payroll') 
    
class ReceiptListView(ListView):
    model = Receipt
    template_name = "receipt/receipt_list.html"
    queryset = Receipt.objects.all()
    paginate_by = 10


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
    
class ReceiptUpdateView(SuccessMessageMixin, UpdateView):                                 
    model = Receipt                                                                      
    form_class = ReceiptForm                                                             
    template_name = "receipt/edit_receipt.html"                                            
    success_url = '/finance/receipt'                                                        
    success_message = "Receipt has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Receipt'
        context["savebtn"] = 'Update Receipt'
        context["delbtn"] = 'Delete Receipt'
        return context

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
    success_url = '/finance/payment'                                                          # redirects to 'inventory' page in the url after submitting the form
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
    
class PaymentUpdateView(SuccessMessageMixin, UpdateView):                                 
    model = Payment                                                                      
    form_class = PaymentForm                                                             
    template_name = "payment/edit_payment.html"                                            
    success_url = '/finance/payment'                                                        
    success_message = "Payment has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Payment'
        context["savebtn"] = 'Update Payment'
        context["delbtn"] = 'Delete Payment'
        return context

    
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


