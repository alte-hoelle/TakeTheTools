from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from .models import CustomImage, CustomUser, Tool


def make_ids_barcode_field() -> None:
    tools = Tool.objects.all()

    for tool in tools:
        tool.barcode_ean13_no_check_bit = str(tool.id)
        print(tool.barcode_ean13_no_check_bit)
        tool.save()


def create_custom_user_models() -> None:
    users = get_user_model().objects.all()
    for user in users:
        newcustomuser = CustomUser(
            user=user, chip_id=make_password(str(user.id)[1:-1], settings.CHIP_SALT)
        )

        newcustomuser.save()


def migrate_pictures() -> None:
    tools = Tool.objects.all()
    for tool in tools:
        image = CustomImage(supplied_source=tool.used_img_urls)
        image.save(
            "/home/stoerte/Software/django-begin/src/staticfiles/"
            + str(tool.img_local_link)
        )
        tool.img = image
        tool.save()
