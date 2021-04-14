import django_tables2 as tables
from .models import Tool, Note

ATTRS = {"class": "table table-responsive table-striped table-hover"}

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
        attrs = ATTRS
        fields = (
            "barcode_ean13_no_check_bit",
            "name",
            "brand",
            "model",
            "owner",
            "description",
        )

class UserTable(LenditTable):
    # We cannot use the definition via Meta here,
    # as the Usermodel cannot be imported, but needs
    # to be fetched with get_user_model()
    username = tables.Column()
    email = tables.Column()

class NoteTable(tables.Table):

    class Meta:
        model = Note
        attrs = ATTRS
        fields = (
            "title",
            "author",
            "text",
            "prio",
        )

