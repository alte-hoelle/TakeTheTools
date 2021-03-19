import django_tables2 as tables

from .models import Tool

ATTRS = {"class": "table table-responsive table-striped"}


class LenditTable(tables.Table):
    class Meta:
        attrs = ATTRS


class ToolTable(LenditTable):
    class Meta:
        model = Tool
        fields = (
            "barcode_ean13_no_check_bit",
            "name",
            "brand",
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
