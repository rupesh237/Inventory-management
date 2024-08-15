from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View,
    CreateView, 
    UpdateView,
    ListView,
)
from django.db import models
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .models import Stock, StockTransfer
from .forms import StockForm, StockTransferForm
from django_filters.views import FilterView
from .filters import StockFilter

from django.apps import apps


class StockListView(FilterView):
    filterset_class = StockFilter
    template_name = 'inventory.html'
    paginate_by = 10

    def get_queryset(self):
        # Assuming you have a way to get the branch associated with the user
        user_branch = self.request.user.profile.branch
        return Stock.objects.filter(is_deleted=False, branch=user_branch).order_by('-id')


class StockCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Stock                                                                       # setting 'Stock' model as model
    form_class = StockForm                                                              # setting 'StockForm' form as form
    template_name = "add_stock.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Stock has been created successfully"                             # displays message when form is submitted
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Stock'
        context["savebtn"] = 'Add to Inventory'
        return context  
        

class StockUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
    model = Stock                                                                       # setting 'Stock' model as model
    form_class = StockForm                                                              # setting 'StockForm' form as form
    template_name = "edit_stock.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Stock has been updated successfully"                             # displays message when form is submitted

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Stock'
        context["savebtn"] = 'Update'
        context["delbtn"] = 'Delete'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        print("Form is valid. Stock updated.")
        return response


class StockDeleteView(View):                        
    template_name = "delete_stock.html"                                                 
    success_message = "Stock has been deleted successfully"                            
    
    def get(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        return render(request, self.template_name, {'object' : stock})

    def post(self, request, pk):  
        stock = get_object_or_404(Stock, pk=pk)
        PurchaseItem = apps.get_model('transactions', 'PurchaseItem')
        SaleItem = apps.get_model('transactions', 'SaleItem')
        if PurchaseItem.objects.filter(stock=stock).exists() or SaleItem.objects.filter(stock=stock).exists():
            messages.error(request,"Cannot delete stock item that is referenced in purchases or sales.")
            return redirect('inventory')
        else:
            stock.delete()                                             
            messages.success(request, self.success_message)
            return redirect('inventory')
        
class StockTransferView(View):
    def get(self, request):
        form = StockTransferForm(user=request.user)
        return render(request, 'stock_transfer.html', {'form': form})

    def post(self, request):
        form = StockTransferForm(request.POST, user=request.user)
        if form.is_valid():
            stock_transfer = form.save(commit=False)
            stock_transfer.transferred_by = request.user
            stock_transfer.save()
            messages.success(request, "Stock has been transferred successfully for processing.")
            return redirect('stock-transfer-list')
        return render(request, 'stock_transfer.html', {'form': form})
    
class StockTransferListView(ListView):
    model = StockTransfer
    template_name = 'stock_transfer_list.html' 
    paginate_by = 10  # Adjust pagination as needed

    def get_queryset(self):
        user_branch = self.request.user.profile.branch
        # Filter StockTransfer objects where the user's branch is either the to_branch or from_branch
        queryset = StockTransfer.objects.filter(
            models.Q(to_branch=user_branch) | models.Q(from_branch=user_branch)
        ).order_by('-transfer_date')
        return queryset
    
def update_transfer_status(request, transfer_id, action):
    transfer = get_object_or_404(StockTransfer, id=transfer_id)

    if transfer.status == 'pending':
        if action == 'received':
            transfer.status = 'received'
            # Update stock quantities
            try:
                # Deduct quantity from from_branch stock
                stock_item_from = Stock.objects.get(id=transfer.stock.id, branch=transfer.from_branch)
                stock_item_from.quantity -= transfer.quantity
                stock_item_from.save()

                # Add quantity to to_branch stock
                stock_item_to, created = Stock.objects.get_or_create(
                    name=transfer.stock.name,
                    branch=transfer.to_branch,
                    defaults={
                        'category': transfer.stock.category,
                        'price': transfer.stock.price,
                        'placed_at': transfer.stock.placed_at,
                        'created_by': transfer.stock.created_by,
                        'unit': transfer.stock.unit,
                        'quantity': transfer.quantity  # Initialize quantity if new stock
                    }
                )
                if not created:
                    stock_item_to.quantity += transfer.quantity
                stock_item_to.save()

                messages.success(request, f"Stock {transfer.stock.name} has been received successfully.")
            except ValueError as e:
                messages.error(request, str(e))

        elif action == 'cancelled':
            transfer.status = 'cancelled'
            messages.info(request, f"Stock transfer of {transfer.stock.name} has been cancelled.")
        else:
            messages.error(request, "Invalid action specified.")
        
        transfer.save()
    else:
        messages.warning(request, "This transfer is not pending or has already been processed.")

    return redirect('stock-transfer-list')  

