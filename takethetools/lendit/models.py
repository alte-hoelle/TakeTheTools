from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=30)
    needs_power = models.BooleanField(default=False)
    needs_battery = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name

class Tool(models.Model):
    name = models.CharField(max_length=30)
    model = models.CharField(max_length=30, default="", blank=True)
    brand = models.CharField(max_length=30)
    category = models.ForeignKey(Category, default=None, null=True, on_delete=models.CASCADE)
    price = models.IntegerField()
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, default=0, on_delete=models.SET_DEFAULT)
    available_amount = models.IntegerField()
    present_amount = models.IntegerField(default=1)
    sec_class = models.IntegerField()
    trust_class = models.IntegerField()
    buy_date = models.DateField(default=timezone.now, null=True, blank=True)
    img_local_link = models.CharField(max_length=120, default="", blank=True, null=True)
    used_img_urls = models.URLField(default="", blank=True)
    barcode_ean13_no_check_bit = models.CharField(max_length=12, default="999999999999")

    def __str__(self):
        return str(self.name) + " " + str(self.brand)

class Purpose(models.Model):
    name = models.CharField(max_length=30)
    multiplier = models.FloatField()

    def __str__(self):
        return(self.name)


class Lendlog(models.Model):
    tool = models.ForeignKey(Tool, default=0, on_delete=models.CASCADE)
    from_date = models.DateField(default=timezone.now)
    expected_end_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True, default=timezone.now)
    status = models.IntegerField(default=False)
    lend_by = models.ForeignKey(settings.AUTH_USER_MODEL, default=0, on_delete=models.CASCADE, related_name="lender")
    returned_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, default=0, on_delete=models.CASCADE,
                                    related_name="returner")
    purpose = models.ForeignKey(Purpose, default=0, on_delete=models.SET_DEFAULT)
    return_comment = models.CharField(max_length=120, default="")
    lend_comment = models.CharField(max_length=120, default="")

    def __str__(self):
        return "Tool " + self.tool.name + " by " + str(self.lend_by)
