from .models import Tool

def make_ids_barcode_field():
    tools = Tool.objects.all()

    for tool in tools:
        tool.barcode_ean13_no_check_bit = str(tool.id)
        print(tool.barcode_ean13_no_check_bit)
        tool.save()

