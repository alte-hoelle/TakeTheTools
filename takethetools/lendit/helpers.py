from .models import Tool, CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings

def make_ids_barcode_field():
    tools = Tool.objects.all()

    for tool in tools:
        tool.barcode_ean13_no_check_bit = str(tool.id)
        print(tool.barcode_ean13_no_check_bit)
        tool.save()

def create_custom_user_models():
    users = get_user_model().objects.all()
    for user in users:
        newcustomuser = CustomUser(
            user = user,
            chip_id = make_password(str(user.id)[1:-1], settings.CHIP_SALT)
        )

        newcustomuser.save()
