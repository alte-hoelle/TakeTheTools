from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from PIL import Image
import requests

from .utils import gen_random_ean13_no_checkbit


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chip_id = models.CharField(max_length=512)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=30)
    needs_power = models.BooleanField(default=False)
    needs_battery = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class CustomImage(models.Model):
    image = models.ImageField(upload_to='icons')
    supplied_source = models.URLField(default="", blank=True)
    description = models.CharField(max_length=100, default="", blank=True)
    default = models.BooleanField(default=True)

    def __str__(self):
        return str(self.image)

    def save(self, path='',filename="", *args, **kwargs):
        if path in (None, "") and filename in (None, ""):
            super(CustomImage, self).save(*args, **kwargs)
        else:
            if "http" in path:

                r = requests.get(path, stream=True)
                if r.status_code == 200:

                    r.raw.decode_content = True
                    im = Image.open(r.raw)
                    im.thumbnail((60, 60), Image.ANTIALIAS)
                    im.save("media/icons/" + filename)

                else:
                    return False

            else:
                return False
                # Implement local picture uploading
                #try:
                #    pilimage = Image.open(path)
                #except:
                #    pilimage = Image.open("/home/stoerte/Software/django-begin/takethetools/staticfiles/img/tool_icons/default.png")

            try:
                self.image = "icons/" + filename

            except Exception as e:
                return False
            super(CustomImage, self).save(*args, **kwargs)

            return True


class Tool(models.Model):
    name = models.CharField(max_length=30)
    model = models.CharField(max_length=30, default="", blank=True)
    brand = models.CharField(max_length=30)
    category = models.ForeignKey(
        Category, default=None, null=True, on_delete=models.CASCADE
    )
    price = models.IntegerField()
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, default=0, on_delete=models.SET_DEFAULT
    )
    available_amount = models.IntegerField()
    present_amount = models.IntegerField(default=1)
    sec_class = models.IntegerField()
    trust_class = models.IntegerField()
    buy_date = models.DateField(default=timezone.now, null=True, blank=True)
    img = models.ForeignKey(
        CustomImage,
        default=None,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    barcode_ean13_no_check_bit = models.CharField(
        unique=True, max_length=12, default=gen_random_ean13_no_checkbit
    )

    def __str__(self):
        return str(self.name) + " " + str(self.brand)


class Purpose(models.Model):
    name = models.CharField(max_length=30)
    multiplier = models.FloatField()

    def __str__(self):
        return self.name


class Lendlog(models.Model):
    tool = models.ForeignKey(Tool, default=0, on_delete=models.CASCADE)
    from_date = models.DateField(default=timezone.now)
    expected_end_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True, default=timezone.now)
    status = models.IntegerField(default=False)
    lend_by = models.ForeignKey(
        CustomUser,
        default=0,
        on_delete=models.CASCADE,
        related_name="lender",
    )
    returned_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        default=0,
        on_delete=models.CASCADE,
        related_name="returner",
    )

    purpose = models.ForeignKey(Purpose, default=0, on_delete=models.SET_DEFAULT)
    return_comment = models.CharField(max_length=120, default="")
    lend_comment = models.CharField(max_length=120, default="")

    def __str__(self):
        return "Tool " + self.tool.name + " by " + str(self.lend_by)
