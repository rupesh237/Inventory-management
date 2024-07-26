import django_filters
from .models import Payroll    

class PayrollFilter(django_filters.FilterSet):                         
    # period_start = django_filters.DateFilter(field_name='period_start', lookup_expr='gte', label='From')
    paid_date = django_filters.DateFilter(field_name='paid_date', lookup_expr='lte')          
    class Meta:
        model = Payroll
        fields = ['paid_date']