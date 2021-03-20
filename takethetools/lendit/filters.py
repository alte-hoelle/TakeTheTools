import django_filters as filters
from .models import Tool

ATTRS = {"class": "table table-responsive table-striped"}

class LenditFilter(filters.Filter):
    pass

class ToolFilter(filters.FilterSet):

    class Meta:
        model = Tool
        fields = {
            'name':['contains'],
            'model':['contains'],
            'brand':['contains'],
            'barcode_ean13_no_check_bit':['exact']
        }