from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View, 
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    PurchaseBill, 
    Supplier, 
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,  
    SaleItem,
    SaleBillDetails
)
from .forms import (
    SelectSupplierForm, 
    PurchaseItemFormset,
    PurchaseDetailsForm, 
    SupplierForm, 
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm
)
from inventory.models import Stock
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_date




# shows a lists of all suppliers
class SupplierListView(ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    queryset = Supplier.objects.filter(is_deleted=False)
    paginate_by = 10


# used to add a new supplier
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier has been created successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Supplier'
        context["savebtn"] = 'Add Supplier'
        return context     


# used to update a supplier's info
class SupplierUpdateView(SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier details has been updated successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Supplier'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Supplier'
        return context


# used to delete a supplier
class SupplierDeleteView(View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "Supplier has been deleted successfully"

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object' : supplier})

    def post(self, request, pk):  
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.save()                                               
        messages.success(request, self.success_message)
        return redirect('suppliers-list')


# used to view a supplier's profile
class SupplierView(View):
    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier'  : supplierobj,
            'bills'     : bills
        }
        return render(request, 'suppliers/supplier.html', context)




# shows the list of bills of all purchases 
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10


# used to select the supplier
class SelectSupplierView(View):
    form_class = SelectSupplierForm
    template_name = 'purchases/select_supplier.html'

    def get(self, request, *args, **kwargs):                                    # loads the form page
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):                                   # gets selected supplier and redirects to 'PurchaseCreateView' class
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get("supplier")
            supplier = get_object_or_404(Supplier, id=supplierid)
            return redirect('new-purchase', supplier.pk)
        return render(request, self.template_name, {'form': form})


# used to generate a bill object and save items
class PurchaseCreateView(View):                                                 
    template_name = 'purchases/new_purchase.html'

    def get(self, request, pk):
        formset = PurchaseItemFormset(request.GET or None)              # renders an empty formset
        supplierobj = get_object_or_404(Supplier, pk=pk)  # gets the supplier object
        current_date = datetime.date(datetime.now())                  
        context = {
            'formset'   : formset,
            'supplier'  : supplierobj,
            'current_date' : current_date,
        }                                                                       # sends the supplier and formset as context
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = PurchaseItemFormset(request.POST)                             # recieves a post method for the formset
        supplierobj = get_object_or_404(Supplier, pk=pk)                     # gets the supplier object
        if formset.is_valid():
            # saves bill
            bill_no = request.POST['purchase-bill']
            purchase_discount = request.POST['purchase-discount']
            purchase_date_str = request.POST['purchase-date']
            purchase_date = parse_date(purchase_date_str) if purchase_date_str else timezone.now()
            print(purchase_date)

            if purchase_date is not None:
               if bill_no:
                   billobj = PurchaseBill(supplier=supplierobj, billno=bill_no, time=purchase_date, prepared_by=request.user) 
               else:
                   billobj = PurchaseBill(supplier=supplierobj, time=purchase_date, prepared_by=request.user) 
            else: 
                if bill_no:
                   billobj = PurchaseBill(supplier=supplierobj, billno=bill_no, prepared_by=request.user)  
                else:
                   billobj = PurchaseBill(supplier=supplierobj, prepared_by=request.user)  
            billobj.save()                                                      # saves object into the db
            for form in formset:                                                # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj                                       # links the bill object to the items
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)       # gets the item
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity += billitem.quantity                              # updates quantity
                # saves bill item and stock
                stock.save()
                billitem.save()
            #create bill details object
            billdetailsobj = PurchaseBillDetails(billno=billobj, discount_percentage=purchase_discount)
            billdetailsobj.get_total_amount_with_taxes()
            billdetailsobj.save()
            messages.success(request, "Purchased items have been registered successfully")
            return redirect('purchase-bill', billno=billobj.billno)
        formset = PurchaseItemFormset(request.GET or None)
        context = {
            'formset'   : formset,
            'supplier'  : supplierobj
        }
        return render(request, self.template_name, context)


# used to delete a bill object
class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "purchases/delete_purchase.html"
    success_url = '/transactions/purchases'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Purchase bill has been deleted successfully")
        return super(PurchaseDeleteView, self).delete(*args, **kwargs)




# shows the list of bills of all sales 
class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10


# used to generate a bill object and save items
class SaleCreateView(View):                                                      
    template_name = 'sales/new_sale.html'

    def get(self, request):
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)                          # renders an empty formset
        stocks = Stock.objects.filter(is_deleted=False)
        context = {
            'form'      : form,
            'formset'   : formset,
            'stocks'    : stocks
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)                                 # recieves a post method for the formset
        if form.is_valid() and formset.is_valid():
            sale_discount = request.POST['sale-discount']
            # saves bill
            billobj = form.save(commit=False)
            billobj.prepared_by = request.user
            billobj.save()     
            for form in formset:                                          # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj                                       # links the bill object to the items
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)      
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity -= billitem.quantity   
                # saves bill item and stock
                stock.save()
                billitem.save()
            # create bill details object
            billdetailsobj = SaleBillDetails(billno=billobj, discount_percentage=sale_discount)
            billdetailsobj.get_total_amount_with_taxes()
            billdetailsobj.save()
            messages.success(request, "Sold items have been registered successfully")
            return redirect('sale-bill', billno=billobj.billno)
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        context = {
            'form'      : form,
            'formset'   : formset,
        }
        return render(request, self.template_name, context)


# used to delete a bill object
class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transactions/sales'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Sale bill has been deleted successfully")
        return super(SaleDeleteView, self).delete(*args, **kwargs)




# used to display the purchase bill object
class PurchaseBillView(View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        context = {
            'bill'          : PurchaseBill.objects.get(billno=billno),
            'items'         : PurchaseItem.objects.filter(billno=billno),
            'billdetails'   : PurchaseBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj, created = PurchaseBillDetails.objects.get_or_create(billno=billno)

            # Update billdetailsobj with form data
            billdetailsobj.eway = form.cleaned_data.get('eway')
            billdetailsobj.veh = form.cleaned_data.get('veh')
            billdetailsobj.destination = form.cleaned_data.get('destination')
            billdetailsobj.po = form.cleaned_data.get('po')
            billdetailsobj.cgst = form.cleaned_data.get('cgst')
            billdetailsobj.sgst = form.cleaned_data.get('sgst')
            billdetailsobj.igst = form.cleaned_data.get('igst')
            billdetailsobj.cess = form.cleaned_data.get('cess', 0)  # Handle default value if cess is not provided
            billdetailsobj.tcs = form.cleaned_data.get('tcs')
            billdetailsobj.discount_amount = form.cleaned_data.get('discount_amount')
            billdetailsobj.total = form.cleaned_data.get('total')
            billdetailsobj.paid_amount = form.cleaned_data.get('paid_amount', 0)
            billdetailsobj.due_amount = form.cleaned_data.get('due_amount', 0)

            print(billdetailsobj.cess)
            if billdetailsobj.cess is not None:
               billdetailsobj.get_total_amount_with_taxes()
            if billdetailsobj.discount_amount is not None:
               if billdetailsobj.cess is None:
                   billdetailsobj.cess = 0.0
               billdetailsobj.get_total_amount_with_taxes()
            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        else:
             # Print form errors to debug
            print(form.errors)
            messages.error(request, "Form is not valid")
        context = {
            'bill'          : PurchaseBill.objects.get(billno=billno),
            'items'         : PurchaseItem.objects.filter(billno=billno),
            'billdetails'   : PurchaseBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)


# used to display the sale bill object
class SaleBillView(View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"
    
    def get(self, request, billno):
        context = {
            'bill'          : SaleBill.objects.get(billno=billno),
            'items'         : SaleItem.objects.filter(billno=billno),
            'billdetails'   : SaleBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = SaleBillDetails.objects.get(billno=billno)
            
           # Update billdetailsobj with form data
            billdetailsobj.eway = form.cleaned_data.get('eway')
            billdetailsobj.veh = form.cleaned_data.get('veh')
            billdetailsobj.destination = form.cleaned_data.get('destination')
            billdetailsobj.po = form.cleaned_data.get('po')
            billdetailsobj.cgst = form.cleaned_data.get('cgst')
            billdetailsobj.sgst = form.cleaned_data.get('sgst')
            billdetailsobj.igst = form.cleaned_data.get('igst')
            billdetailsobj.cess = form.cleaned_data.get('cess', 0)  # Handle default value if cess is not provided
            billdetailsobj.tcs = form.cleaned_data.get('tcs')
            billdetailsobj.discount_amount = form.cleaned_data.get('discount_amount')
            billdetailsobj.total = form.cleaned_data.get('total')
            billdetailsobj.paid_amount = form.cleaned_data.get('paid_amount', 0)
            billdetailsobj.due_amount = form.cleaned_data.get('due_amount', 0)

            print(billdetailsobj.cess)
            if billdetailsobj.cess is not None:
               billdetailsobj.get_total_amount_with_taxes()  # Ensure this method calculates correctly
            if billdetailsobj.discount_amount is not None:
               if billdetailsobj.cess is None:
                   billdetailsobj.cess = 0.0
               billdetailsobj.get_total_amount_with_taxes()
            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        else:
             # Print form errors to debug
            print(form.errors)
            messages.error(request, "Form is Invaid.")
        context = {
            'bill'          : SaleBill.objects.get(billno=billno),
            'items'         : SaleItem.objects.filter(billno=billno),
            'billdetails'   : SaleBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)