from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic import View, TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.models import User
from .models import UserProfile

from inventory.models import Stock
from transactions.models import SaleBill, PurchaseBill, SaleItem, PurchaseItem

from .models import Company, Branch
from .forms import BranchForm, UserCreationWithProfileForm

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
        branch = self.request.user.profile.branch

        # Data for purchase-graph
        purchase_bills = PurchaseBill.objects.filter(time__gte=six_months_ago, time__lte=today)
        for bill in purchase_bills:
            purchase_items = PurchaseItem.objects.filter(billno=bill.billno, branch=branch)
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
            sale_items = SaleItem.objects.filter(billno=bill.billno, branch=branch)
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

        stockqueryset = Stock.objects.filter(branch=branch, is_deleted=False).order_by('-quantity')
        for item in stockqueryset:
            labels.append(item.name)
            data.append(item.quantity)

        # Get the latest 3 sales for the specific branch
        sales = SaleBill.objects.filter(salebillno__branch=branch).order_by('-time')[:3]

        # Get the latest 3 purchases for the specific branch
        purchases = PurchaseBill.objects.filter(purchasebillno__branch=branch).order_by('-time')[:3]

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

class BranchListView(ListView):
    model = Branch
    template_name = "branches/branch_list.html"
    queryset = Branch.objects.all().order_by('id')
    paginate_by = 10


# used to add a new supplier
class BranchCreateView(SuccessMessageMixin, CreateView):
    model = Branch
    form_class = BranchForm
    success_url = '/branches'
    success_message = "Branch has been created successfully."
    template_name = "branches/edit_branch.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Branch'
        context["savebtn"] = 'Add Branch'
        return context   

    def get_form_kwargs(self):
        """Pass the request object to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Add the request to the form kwargs
        return kwargs  


class BranchUpdateView(SuccessMessageMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    success_url = '/branches'
    success_message = "Branch details has been updated successfully"
    template_name = "branches/edit_branch.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Branch'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Branch'
        return context


# used to delete a supplier
class BranchDeleteView(View):
    template_name = "branches/delete_branch.html"
    success_message = "Branch has been deleted successfully."

    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        return render(request, self.template_name, {'object' : branch})

    def post(self, request, pk):  
        branch = get_object_or_404(Branch, pk=pk)
        users = User.objects.filter(profile__branch=branch)
        # Delete each user and their associated profile
        for user in users:
            user.delete() 
        branch.delete()                                              
        messages.success(request, self.success_message)
        return redirect('branch-list')
    

class BranchView(View):
    def get(self, request, name):
        branchobj = get_object_or_404(Branch, name=name)
        user_list = UserProfile.objects.filter(branch=branchobj).order_by('-user_id')
        page = request.GET.get('page', 1)
        paginator = Paginator(user_list, 10)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        context = {
            'branch'  : branchobj,
            'users'     : users,
        }
        return render(request, 'branches/branch.html', context)
    

class UserCreateView(SuccessMessageMixin, CreateView):
    form_class = UserCreationWithProfileForm
    success_url = '/branches'
    success_message = "User has been created successfully."
    template_name = 'users/add_user.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        branch = get_object_or_404(Branch, id=self.kwargs['branch_id'])
        kwargs['branch'] = branch
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print("Form is invalid.")
        print(form.errors)  
        return super().form_invalid(form)
    
    def get_success_url(self):
        branch = self.object.profile.branch  # assuming the User has a related profile with a branch
        return reverse('branch_profile', kwargs={'name': branch.name})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New User'
        context["savebtn"] = 'Add User'
        return context
        
    
class UserUpdateView(SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserCreationWithProfileForm
    template_name = 'users/add_user.html'
    success_url = '/branches'
    success_message = "User details has been updated successfully."

    def get_success_url(self):
        branch = self.object.profile.branch  # assuming the User has a related profile with a branch
        return reverse('branch_profile', kwargs={'name': branch.name})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit User'
        context["savebtn"] = 'Save Changes'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'branch_id' in self.kwargs:
            branch = get_object_or_404(Branch, id=self.kwargs['branch_id'])
        else:
            user = self.get_object()
            branch = user.profile.branch
        kwargs['branch'] = branch
        return kwargs

    
class UserDeleteView(View):
    template_name = "users/delete_user.html"
    success_message = "User has been deleted successfully"

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, self.template_name, {'object' : user})

    def post(self, request, pk):  
        user = get_object_or_404(User, pk=pk)
        branch = user.profile.branch
        user.delete()                                               
        messages.success(request, self.success_message)
        return redirect('branch-list')
    
    def get_success_url(self):
        branch = self.object.profile.branch  # assuming the User has a related profile with a branch
        return reverse('branch_profile', kwargs={'name': branch.name})


