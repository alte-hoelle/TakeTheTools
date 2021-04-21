import django_tables2 as tables
from django.utils.html import format_html

from .models import Tool

ATTRS = {"class": "table table-responsive table-striped table-hover"}


class LenditTable(tables.Table):
    class Meta:
        attrs = ATTRS


class ToolTable(tables.Table):

    image = tables.TemplateColumn('<img src="/media/{{record.img}}" style="width:60px;"> ')
    my_column = tables.TemplateColumn(verbose_name='Auswählen',
                                      template_name='tool_table_button.html',
                                      orderable=False)  # orderable not sortable

    class Meta:
        model = Tool
        attrs = ATTRS
        fields = (
            "name",
            "brand",
            "model",
            "owner",
            "description",
            "present_amount"
        )
        sequence = ('image', 'name', 'brand', 'model', 'owner', 'description', 'present_amount', 'my_column')


class UserTable(LenditTable):
    # We cannot use the definition via Meta here,
    # as the Usermodel cannot be imported, but needs
    # to be fetched with get_user_model()
    id = tables.Column()
    username = tables.Column()
    email = tables.Column()
