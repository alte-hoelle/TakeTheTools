import django_tables2 as tables

from .models import Tool

ATTRS = {'class': 'table table-responsive table-striped'}


class ToolTable(tables.Table):
    class Meta:
        model = Tool
        fields = ('barcode_ean13_no_check_bit', 'name', 'brand', 'owner', 'sec_class', 'description')
        attrs = ATTRS
