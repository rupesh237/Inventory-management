from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    View,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django_filters.views import FilterView

from .models import Employee, Payroll
from .forms import EmployeeForm, PayrollForm

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

class EmployeeUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
    model = Employee                                                                       # setting 'Stock' model as model
    form_class = EmployeeForm                                                              # setting 'StockForm' form as form
    template_name = "employee/edit_employee.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/finance/employee'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Employee's details has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Employee'
        context["savebtn"] = 'Update Employee'
        context["delbtn"] = 'Delete Employee'
        return context


class EmployeeDeleteView(View):                                                            # view class to delete stock
    template_name = "employee/delete_employee.html"                                                 # 'delete_stock.html' used as the template
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

class PayrollUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
    model = Payroll                                                                       # setting 'Stock' model as model
    form_class = PayrollForm                                                              # setting 'StockForm' form as form
    template_name = "payroll/edit_payroll.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/finance/payroll'                                                          # redirects to 'inventory' page in the url after submitting the form
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