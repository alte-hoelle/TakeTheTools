from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from PIL import Image
from io import StringIO
from django.core.files.base import ContentFile

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

    def save(self, path='', *args, **kwargs):
        try:
            pilimage = Image.open(path)
        except:
            pilimage = Image.open("/home/stoerte/Software/django-begin/takethetools/staticfiles/img/tool_icons/default.png")

        try:
            filename = path.split("/")[-1]
            self.image = filename
            tempfile = pilimage

            tempfile_io = StringIO()

            #tempfile.save(filename, format=pilimage.format)

            self.image.save(filename, ContentFile(tempfile_io.getvalue()), save=False)
        except Exception as e:
            print("Error saving Image", e)

        super(CustomImage, self).save(*args, **kwargs)


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
    img_local_link = models.CharField(max_length=120, default="", blank=True, null=True)
    img = models.ForeignKey(
        CustomImage,
        default=None,#CustomImage.objects.get(description="Default"),
        on_delete=models.SET_DEFAULT,
        blank=True,
        null=True
    )
    used_img_urls = models.URLField(default="", blank=True)
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
