from .models import Tool, CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
import string, random

def make_ids_barcode_field():
    tools = Tool.objects.all()

    for tool in tools:
        tool.barcode_ean13_no_check_bit = str(tool.id)
        print(tool.barcode_ean13_no_check_bit)
        tool.save()

def create_custom_user_models():
    users = get_user_model().objects.all()
    for user in users:
        salt = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        newcustomuser = CustomUser(
            user = user,
            chip_id = make_password(str(user.id)[1:-1], salt),
            chip_salt = salt
        )
        newcustomuser.save()
