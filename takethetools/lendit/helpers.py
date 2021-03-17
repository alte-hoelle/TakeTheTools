from .models import Tool, CustomUser, CustomImage
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings

from PIL import Image

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

def migrate_pictures():
    tools = Tool.objects.all()
    for tool in tools:
        im = CustomImage(
            supplied_source=tool.used_img_urls
        )
        print("/home/stoerte/Software/django-begin/takethetools/static/" + tool.img_local_link)
        im.save("/home/stoerte/Software/django-begin/takethetools/staticfiles/" + str(tool.img_local_link))
        tool.img = im
        tool.save()



