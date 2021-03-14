import string
import random

from datetime import datetime
from django_tables2 import SingleTableView

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from lendit.forms import (
    ExportSelectionForm,
    CheckoutForm,
    CheckinForm,
    AddItemToCartIDForm,
    UserRegistrationForm,
    ToolRegistrationForm,
    UserRegistrationFormChip,
)
from lendit.models import Tool, Lendlog, Purpose
from lendit.tables import ToolTable, UserTable


class ToolList(SingleTableView):
    template_name = "tool_list.html"
    queryset = Tool.objects.all()
    table_class = ToolTable


class UserList(SingleTableView):
    template_name = "user_list.html"
    table_class = UserTable

    def get_queryset(self, *args, **kwargs):
        User = get_user_model()
        return User.objects.all()


class Home(TemplateView):
    template_name = "home.html"


class ToolCreate(CreateView):
    model = Tool
    form_class = ToolRegistrationForm
    success_url = reverse_lazy('tools')
    template_name = 'tool_reg.html'


def Overview(request):
    active = Lendlog.objects.filter(status=1)
    inactive = Lendlog.objects.filter(status=0)

    context = {"active": active, "returned": inactive}
    return render(request, "stats.html", context)


def registerUser(request):
    context = {"form": UserRegistrationForm, "form_chip": UserRegistrationFormChip}
    return render(request, "user_reg.html", context)


def addUser(request):

    form = UserRegistrationForm(request.POST)
    form_chip = UserRegistrationFormChip(request.POST)

    if form.is_valid():
        User = get_user_model()

        newuser = User(
            id=random.randint(1000000, 9999999),
            password="",
            last_login=datetime.now(),
            is_superuser=0,
            username=form.cleaned_data["username"],
            last_name="",
            email=form.cleaned_data["email"],
            is_staff=0,
            is_active=1,
            date_joined=datetime.now(),
            first_name="",
        )
        newuser.set_password(form.cleaned_data["password"])
        newuser.save()
        return redirect("users")
    elif form_chip.is_valid():
        User = get_user_model()
        newuser = User(
            password="",
            last_login=datetime.now(),
            is_superuser=0,
            username=form_chip.cleaned_data["username"],
            last_name="",
            email=form_chip.cleaned_data["email"],
            is_staff=0,
            is_active=1,
            date_joined=datetime.now(),
            first_name="",
        )

        output_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
        newuser.set_password(output_string)
        newuser.save()
        newcustomuser = CustomUser(
            user = newuser,
            chip_id =  make_password(form_chip.cleaned_data["chip_id"], settings.CHIP_SALT)
        )


        newuser.set_password(output_string)
        newcustomuser.save()

        return redirect('users')
    else:
        return redirect("index")



def lendTool(barcode=0, end=datetime.today(), lender=0, purpose="Verein"):

    current_tool = Tool.objects.get(barcode_ean13_no_check_bit=barcode)
    purpose = Purpose.objects.get(name=purpose)
    try:
        user = CustomUser.objects.get(chip_id = lender)
    except Exception as e:
        return False, "User was not found"

    newlog = Lendlog(
        tool=current_tool,
        from_date=datetime.today(),
        expected_end_date=end,
        end_date=None,
        status=1,
        lend_by=user,
        returned_by=None,
        purpose=purpose,
    )

    newlog.save()

    current_tool.present_amount = current_tool.present_amount - 1
    current_tool.save()
    return True, ""


def Checkout(request):

    form = CheckoutForm(request.POST)
    form_in = CheckinForm(request.POST)

    ids = request.session["cart"]
    if not ids:

        return redirect("cart")

    if "lend" in request.POST:
        if form.is_valid():

            idlist = ids.split(",")
            for id in idlist:
                ok, msg = lendTool(barcode=id,
                         purpose=form.cleaned_data["purpose"],
                         end=form.cleaned_data["expected_end"],
                         lender= make_password(form.cleaned_data["lendby"], settings.CHIP_SALT))


                if not ok:
                    messages.error(request, msg)
                    return redirect("cart")

            clearbasket(request)
            messages.success(request, "Alles ausgeliehen!")

    elif "return" in request.POST:

        if form_in.is_valid():
            try:

                returner = CustomUser.objects.get(chip_id = make_password(form_in.cleaned_data["returned_by"], settings.CHIP_SALT))

            except Exception as e:
                messages.error(request, "User/Chip ID not found")
                return
            lends_by_id = Lendlog.objects.filter(lend_by=returner, status=1)
            idlist = ids.split(",")
            return_cnt = 0
            for lend in lends_by_id:
                if str(lend.tool.id) in idlist:
                    lend.returned_by = returner
                    lend.end_date = datetime.today()
                    lend.status = 0
                    idlist.remove(str(lend.tool.barcode_ean13_no_check_bit))
                    return_cnt += 1
                    lend.save()
            if not idlist:
                request.session["cart"] = ""
                messages.success(
                    request, "Alle " + str(return_cnt) + " Werkzeuge zurück gegeben"
                )
            else:
                request.session["cart"] = ",".join([str(item) for item in idlist])
                messages.warning(
                    request,
                    str(return_cnt)
                    + " Werkzeuge zurück gegeben, einige nicht, hast du sie geliehen?",
                )
    else:
        pass
    return redirect("cart")


def addToCart(request):

    form = AddItemToCartIDForm(request.POST or None)

    if "add" in request.POST:
        if form.is_valid():
            barcode = form.cleaned_data["item_id"]
            if len(barcode) == 13:
                toolid = barcode[0:-1]
            elif len(barcode) == 12:
                toolid = barcode
            else:
                messages.error(request, "Kein gültiger Barcode")
                return redirect("cart")

            if Tool.objects.filter(barcode_ean13_no_check_bit=toolid).exists():

                if request.session["cart"]:
                    old = request.session["cart"]
                    request.session["cart"] = old + "," + toolid
                else:
                    request.session["cart"] = toolid

            else:
                messages.error(request, "Kein valider Barcode")
    elif "clear" in request.POST:
        del request.session["cart"]
    return redirect("cart")


def clearbasket(request):
    del request.session["cart"]
    return redirect("cart")


def Cart(request):

    display_dict = {}
    try:
        request.session["cart"]
    except KeyError:
        request.session["cart"] = ""
    if request.session["cart"]:
        display_cart = request.session["cart"].split(",")

        if display_cart:
            i = 1
            for id in display_cart:
                if id:
                    temp_tool = Tool.objects.get(barcode_ean13_no_check_bit=id)
                    display_dict[i] = [
                        temp_tool.name,
                        temp_tool.brand,
                        temp_tool.model,
                        temp_tool.description,
                        temp_tool.owner.username,
                        temp_tool.img_local_link,
                    ]
                    i += 1

    context = {}
    context["add_to_cart"] = AddItemToCartIDForm
    context["checkout_form"] = CheckoutForm
    context["checkin_form"] = CheckinForm

    if display_dict:
        context["cart"] = display_dict
    else:
        context["cart"] = False

    return render(request, "cart.html", context)


def exportBarcodes(request):

    context = {"form": ExportSelectionForm}

    return render(request, "export_barcodes.html", context)


def exportBarcodesPDF(request):

    form = ExportSelectionForm()
    export_sheet = Sheet()

    for field in form.get_interest_fields():
        export_sheet.add_tool(int(field.name))

    export_sheet.list()
    export_sheet.export()
    return redirect("export")
