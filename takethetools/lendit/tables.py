import django_tables2 as tables

from .models import Tool

ATTRS = {'class': 'table table-responsive table-striped'}


class ToolTable(tables.Table):
    class Meta:
        model = Tool
        fields = ('id', 'name', 'brand', 'owner', 'sec_class', 'description')
        attrs = ATTRS
