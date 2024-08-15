from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
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
from django.db.models import Sum
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
    SaleDetailsForm,
)
from inventory.models import Stock, Barcode
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
import threading

import cv2
from PIL import Image
from pyzbar.pyzbar import decode

# shows a lists of all suppliers
class SupplierListView(ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    queryset = Supplier.objects.filter(is_deleted=False).order_by('id')
    paginate_by = 10


# used to add a new supplier
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier has been created successfully."
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
    success_message = "Supplier details has been updated successfully."
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
    success_message = "Supplier has been deleted successfully."

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object' : supplier})

    def post(self, request, pk):  
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.delete()                                               
        messages.success(request, self.success_message)
        return redirect('suppliers-list')


# used to view a supplier's profile
class SupplierView(View):
    def get(self, request, name):
        overall_total_amount = 0
        overall_total_due_amount = 0
        branch = self.request.user.profile.branch
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(purchasebillno__branch=branch, supplier=supplierobj)
        for bill in bill_list:
           # Calculate the total amount and due amount for each bill
            purchase_details = PurchaseBillDetails.objects.filter(billno=bill).aggregate(
                total_amount=Sum('total'),
                total_due_amount=Sum('due_amount')
            )
            overall_total_amount += purchase_details['total_amount']
            overall_total_due_amount += purchase_details['total_due_amount']
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
            'bills'     : bills,
            'overall_total_amount': overall_total_amount,
            'overall_total_due_amount': overall_total_due_amount,
        }
        return render(request, 'suppliers/supplier.html', context)




# shows the list of bills of all purchases 
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

    def get_queryset(self):
        branch = self.request.user.profile.branch
        # Filter the PurchaseBill queryset by branch and order by time
        queryset = PurchaseBill.objects.filter(purchasebillno__branch=branch).order_by('-time')
        return queryset


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
        # PurchaseItemForm(request=request)
        formset = PurchaseItemFormset(form_kwargs={'request': request}) # renders an empty formset
        supplierobj = get_object_or_404(Supplier, pk=pk)  # gets the supplier object
        current_date = datetime.date(datetime.now())
        branch = self.request.user.profile.branch                  
        context = {
            'formset'   : formset,
            'supplier'  : supplierobj,
            'current_date' : current_date,
            'stocks': Stock.objects.filter(branch=branch, is_deleted=False),
        }                                                                       # sends the supplier and formset as context
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = PurchaseItemFormset(request.POST, form_kwargs={'request': request})                             # recieves a post method for the formset
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
                # setting branch
                branch = self.request.user.profile.branch
                print(branch)
                billitem.branch = branch
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
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


# used to delete a bill object
class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "purchases/delete_purchase.html"
    success_url = '/transactions/purchases'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billno=self.object.billno)
        branch = self.request.user.profile.branch
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name, branch=branch)
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

    def get_queryset(self):
        branch = self.request.user.profile.branch
        # Filter the SaleBill queryset by branch and order by time
        queryset = SaleBill.objects.filter(salebillno__branch=branch).order_by('-time')
        return queryset


# used to generate a bill object and save items
def get_customer_details(request):
    name = request.GET.get('name', None)
    branch = request.user.profile.branch
    if name:
        try:
            sale_bill = SaleBill.objects.filter(purchasebillno__branch=branch, name=name).first()
            data = {
                'phone': sale_bill.phone,
                'email': sale_bill.email,
                'address': sale_bill.address,
                'vat_no': sale_bill.vat_no,
            }
        except SaleBill.DoesNotExist:
            data = {'error': 'Customer not found'}
    else:
        data = {'error': 'No name provided'}

    return JsonResponse(data)

def get_stock_price(request):
    stock_id = request.GET.get('stock_id')
    try:
        stock = Stock.objects.get(id=stock_id)
        price = stock.price # adjust based on your model field
    except Stock.DoesNotExist:
        price = None
    return JsonResponse({'price': price})

class SaleCreateView(View):                                                      
    template_name = 'sales/new_sale.html'

    def get(self, request):
        form = SaleForm()
        formset = SaleItemFormset(form_kwargs={'request': request})                          # renders an empty formset
        branch=self.request.user.profile.branch
        stocks = Stock.objects.filter(branch=branch, is_deleted=False)
        print(stocks)
        sale_bills = SaleBill.objects.all()
        context = {
            'form'      : form,
            'formset'   : formset,
            'stocks'    : stocks,
            'sale_bills' : sale_bills,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST, form_kwargs={'request': request})                               # recieves a post method for the formset
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
                # setting branch
                branch = self.request.user.profile.branch
                print(branch)
                billitem.branch = branch 
                # saves bill item and stock
                stock.save()
                billitem.save()
            # create bill details object
            billdetailsobj = SaleBillDetails(billno=billobj, discount_percentage=sale_discount)
            if billobj.vat_no is not None:
                billdetailsobj.cgst = 0.13 * billobj.get_total_price()
                billdetailsobj.tds = 0.015 * billobj.get_total_price()
            else:
                billdetailsobj.cgst = 0.0
                billdetailsobj.tds = 0.0
            billdetailsobj.get_total_amount_with_taxes()
            billdetailsobj.save()
            messages.success(request, "Sold items have been registered successfully")
            return redirect('sale-bill', billno=billobj.billno)
        else:
            print("Form or formset is invalid")
            print(f"Form errors: {form.errors}")
            print(f"Formset errors: {formset.errors}")
        
        # If the form or formset is not valid, re-render the form with errors
        stocks = Stock.objects.filter(is_deleted=False)
        sale_bills = SaleBill.objects.all()
        context = {
            'form'      : form,
            'formset'   : formset,
            'stocks': stocks,
            'sale_bills': sale_bills,
        }
        return render(request, self.template_name, context)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


# used to delete a bill object
class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transactions/sales'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        branch = self.request.user.profile.branch
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name, branch=branch)
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
            'bill_total'    : (PurchaseBill.objects.get(billno=billno)).get_total_price()
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
            billdetailsobj.cess = form.cleaned_data.get('cess')
            billdetailsobj.tds = form.cleaned_data.get('tds')
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
            messages.error(request, "Form is not valid")
        context = {
            'bill'          : PurchaseBill.objects.get(billno=billno),
            'items'         : PurchaseItem.objects.filter(billno=billno),
            'billdetails'   : PurchaseBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
            'bill_total'    : (PurchaseBill.objects.get(billno=billno)).get_total_price()
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
            'bill_total'    : (SaleBill.objects.get(billno=billno)).get_total_price()
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
            billdetailsobj.cess = form.cleaned_data.get('cess')
            billdetailsobj.tds = form.cleaned_data.get('tds')
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
            'bill'          : SaleBill.objects.get(billno=billno),
            'items'         : SaleItem.objects.filter(billno=billno),
            'billdetails'   : SaleBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
            'bill_total'    : (SaleBill.objects.get(billno=billno)).get_total_price()
        }
        return render(request, self.template_name, context)


# Global variable to store the scan result
scan_result = None
scanning_active = False
camera_initialized = False
cap = None

def initialize_camera():
    global cap, camera_initialized
    if not camera_initialized:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Set width
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Set height
        cap.set(cv2.CAP_PROP_FPS, 30)  # Set frame rate if possible
        # Warm up the camera
        for _ in range(10):  # Capture and discard a few frames
            cap.read()
        camera_initialized = True

def release_camera():
    global cap, camera_initialized
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()
        cap = None
        camera_initialized = False
    
@csrf_exempt
def start_scan_product(request):
    global scan_result, scanning_active

    if request.method == 'POST':
        if scanning_active:
            return JsonResponse({'error': 'Scanning already in progress'}, status=400)
        
        scanning_active = True
        scan_result = None

        def scan_product():
            global scan_result, scanning_active
            initialize_camera()

            while scanning_active:
                success, frame = cap.read()
                if not success:
                    scan_result = {'error': 'Failed to capture image'}
                    break
                # Show the webcam feed
                cv2.imshow("Scan Product", frame)
                # Decode barcodes
                for code in decode(frame):
                    barcode_data = code.data.decode('utf-8')
                    # print(barcode_data)
                    product_code = barcode_data[:12]
                    try:
                        barcode_query = Barcode.objects.filter(product_code=product_code).first()
                        if barcode_query:
                            scan_result = {
                                'status': 'Scanning successful.',
                                'stock': barcode_query.product.name,
                                'price_per_item': barcode_query.product.price,
                                'barcode': barcode_data
                            }
                            print(scan_result)
                        else:
                            scan_result = {'error': 'Product not found'}
                        break
                    except Exception as e:
                        scan_result = {'error': str(e)}
                        break

                 # Break loop if scan result is set
                if scan_result is not None:
                    break
                
                # Exit the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            release_camera()
            scanning_active = False

        # Use a thread to run the scan_product function
        threading.Thread(target=scan_product, daemon=True).start()
        return JsonResponse({'status': 'Scanning started'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def scan_product_result(request):
    global scan_result
    if scan_result:
        result = scan_result
        scan_result = None  # Do not reset as we want to keep the last result
        return JsonResponse(result)
    else:
        return JsonResponse({'status': 'Scanning in progress'}, status=202)