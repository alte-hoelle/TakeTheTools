import django_tables2 as tables
from django.utils.html import format_html

from .models import Tool

ATTRS = {"class": "table table-responsive table-striped"}


class LenditTable(tables.Table):
    class Meta:
        attrs = ATTRS

class ToolTable(tables.Table):

    image = tables.TemplateColumn('<img src="/media/{{record.img}}" style="width:60px;"> ')
    my_column = tables.TemplateColumn(verbose_name=('Auswählen'),
                                      template_name='tool_table_button.html',
                                      orderable=False)  # orderable not sortable

    class Meta:
        model = Tool
        fields = (
            "barcode_ean13_no_check_bit",
            "name",
            "brand",
            "model",
            "owner",
            "sec_class",
            "description",
        )

class UserTable(LenditTable):
    # We cannot use the definition via Meta here,
    # as the Usermodel cannot be imported, but needs
    # to be fetched with get_user_model()
    id = tables.Column()
    username = tables.Column()
    email = tables.Column()
