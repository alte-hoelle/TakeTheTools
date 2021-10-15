import random
import string
from datetime import datetime
from typing import Tuple

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, SingleTableView

from .barcode_gen import Sheet
from .filters import ToolFilter
from .forms import (
    AddItemToCartIDForm,
    CheckinForm,
    CheckoutForm,
    ExportSelectionForm,
    NoteForm,
    ToolRegistrationForm,
    UserRegistrationForm,
    UserRegistrationFormChip,
)
from .models import CustomUser, Lendlog, Note, Purpose, Tool
from .tables import LendLogTable, ToolTable, UserTable


class ToolList(SingleTableMixin, FilterView):
    template_name = "tool_list.html"
    model = Tool
    queryset = Tool.objects.all()
    table_class = ToolTable
    filterset_class = ToolFilter


class UserList(SingleTableView):
    template_name = "user_list.html"
    table_class = UserTable

    def get_queryset(self, *_args, **_kwargs):
        user = get_user_model()
        return user.objects.all()


class Home(TemplateView):
    template_name = "home.html"


class Notes(View):
    model = Note
    template_name = "notes.html"
    form_class = NoteForm
    # table_class = NoteTable

    def get(self, request, *args, **kwargs) -> HttpResponse:
        form = self.form_class
        return render(
            request, self.template_name, {"form": form, "notes": self.get_queryset()}
        )

    def post(self, request, *args, **kwargs) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return redirect("notes")

    def get_queryset(self, *args, **kwargs) -> QuerySet:  # pylint: disable=no-self-use
        return Note.objects.order_by("date")


class ToolCreate(CreateView):
    model = Tool
    form_class = ToolRegistrationForm
    success_url = reverse_lazy("tools")
    template_name = "tool_reg.html"


class LendLogView(SingleTableView):
    model = Lendlog
    table_class = LendLogTable
    template_name = "stats.html"

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        return Lendlog.objects.order_by("-status")


def register_user(request: HttpRequest) -> HttpResponse:
    context = {
        "UserRegistrationForm": UserRegistrationForm,
        "UserRegistrationFormChip": UserRegistrationFormChip,
    }
    return render(request, "user_reg.html", context)


def add_user(request: HttpRequest) -> HttpResponse:

    form = UserRegistrationForm(request.POST)
    form_chip = UserRegistrationFormChip(request.POST)

    if form.is_valid():
        user = get_user_model()

        new_user = user(
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
        new_user.set_password(form.cleaned_data["password"])
        new_user.save()
        return redirect("users")

    if form_chip.is_valid():
        user = get_user_model()
        new_user = user(
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

        output_string = "".join(
            random.SystemRandom().choice(string.ascii_letters + string.digits)
            for _ in range(32)
        )
        new_user.set_password(output_string)
        new_user.save()
        new_custom_user = CustomUser(
            user=new_user,
            chip_id=make_password(
                form_chip.cleaned_data["chip_id"], settings.CHIP_SALT
            ),
        )

        new_user.set_password(output_string)
        new_custom_user.save()

        return redirect("users")

    return redirect("index")


def lend_tool(
    barcode: int = 0,
    end: int = datetime.today(),
    chip_id: str = "",
    purpose: str = "Verein",
) -> Tuple[bool, str]:

    current_tool = Tool.objects.get(barcode_ean13_no_check_bit=barcode)
    purpose = Purpose.objects.get(name=purpose)
    try:
        user = CustomUser.objects.get(chip_id=chip_id)
    except Exception:
        return False, "User was not found"
    if current_tool.present_amount <= 0:
        return False, "Tool not present"

    new_log = Lendlog(
        tool=current_tool,
        from_date=datetime.today(),
        expected_end_date=end,
        end_date=None,
        status=1,
        lend_by=user,
        returned_by=None,
        purpose=purpose,
    )

    new_log.save()

    current_tool.present_amount = current_tool.present_amount - 1
    current_tool.save()
    return True, ""


def checkout_lend(request: HttpRequest, form: Form) -> HttpResponse:
    if form.is_valid():
        ids = request.session["cart"]
        id_list = ids.split(",")
        for barcode in id_list:
            is_ok, msg = lend_tool(
                barcode=barcode,
                purpose=form.cleaned_data["purpose"],
                end=form.cleaned_data["expected_end"],
                chip_id=make_password(form.cleaned_data["lendby"], settings.CHIP_SALT),
            )

            if not is_ok:
                # todo: was ist das erwartet verhalten? Halber Cart wird eingecheckt, rest nicht weil fehler? Wie Fehler beheben?
                # evtl besser Fehler merken und alles andere aber einchecken lassen.
                messages.error(request, msg)
                return redirect("cart")

        clearbasket(request)
        messages.success(request, "Ausleihen erfolgreich")
    else:
        messages.error(
            request,
            f"Fehler aufgetreten beim ausleihen: \n {str(form.non_field_errors())}",
        )
    return redirect("cart")


def checkout_return(request: HttpRequest, form_in: Form) -> HttpResponse:
    if form_in.is_valid():
        ids = request.session["cart"]
        try:

            returner = CustomUser.objects.get(
                chip_id=make_password(
                    form_in.cleaned_data["returned_by"], settings.CHIP_SALT
                )
            )

        except Exception:
            messages.error(request, "User/Chip ID not found")
            return redirect("cart")
        lends_by_id = Lendlog.objects.filter(lend_by=returner, status=1)
        id_list = ids.split(",")
        return_cnt = 0
        for lend in lends_by_id:
            if str(lend.tool.barcode_ean13_no_check_bit) in id_list:
                lend.returned_by = returner
                lend.end_date = datetime.today()
                lend.status = 0
                id_list.remove(str(lend.tool.barcode_ean13_no_check_bit))
                return_cnt += 1
                lend.save()

                lend.tool.present_amount += 1
                lend.tool.save()
        if not id_list:
            request.session["cart"] = ""
            messages.success(
                request, "Alle " + str(return_cnt) + " Werkzeuge zurück gegeben"
            )
        else:
            request.session["cart"] = ",".join([str(item) for item in id_list])
            messages.warning(
                request,
                str(return_cnt)
                + " Werkzeuge zurück gegeben, einige nicht, hast du sie geliehen?",
            )
    return redirect("cart")


def checkout(request: HttpRequest) -> HttpResponse:
    # default behavior is redirect("cart")

    form = CheckoutForm(request.POST)
    form_in = CheckinForm(request.POST)
    _cart = AddItemToCartIDForm(request.POST)
    ids = request.session["cart"]

    if not ids:
        return redirect("cart")
    if "lend" in request.POST:
        return checkout_lend(request, form)
    if "return" in request.POST:
        return checkout_return(request, form_in)
    return redirect("cart")


def add_to_cart(request: HttpRequest) -> HttpResponse:

    form = AddItemToCartIDForm(request.POST or None)
    print(form.data)

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


def clearbasket(request: HttpRequest) -> HttpResponse:
    del request.session["cart"]
    return redirect("cart")


def cart(request: HttpRequest) -> HttpResponse:

    display_dict = {}
    try:
        request.session["cart"]
    except KeyError:
        request.session["cart"] = ""
    if request.session["cart"]:
        display_cart = request.session["cart"].split(",")

        if display_cart:
            i = 1
            for item in display_cart:
                if item:
                    temp_tool = Tool.objects.get(barcode_ean13_no_check_bit=item)
                    display_dict[i] = [
                        temp_tool.name,
                        temp_tool.brand,
                        temp_tool.model,
                        temp_tool.description,
                        temp_tool.owner.username,
                        temp_tool.img.image,
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


def export_barcodes(request: HttpRequest) -> HttpResponse:

    context = {"form": ExportSelectionForm}

    return render(request, "export_barcodes.html", context)


def export_barcodes_pdf(request: HttpRequest) -> HttpResponse:

    form = ExportSelectionForm(request.POST or None)
    export_sheet: Sheet = Sheet()

    if form.is_valid():
        for key in form.cleaned_data:
            if form.cleaned_data[key] > 0:
                export_sheet.add_tool(int(key), form.cleaned_data[key])

    export_sheet.list()
    export_sheet.export()
    del export_sheet
    return redirect("export")


def test_view(
    request: HttpRequest, barcode_ean13_no_check_bit: str = "999999999999"
) -> HttpResponse:

    if Tool.objects.filter(
        barcode_ean13_no_check_bit=barcode_ean13_no_check_bit
    ).exists():

        if request.session["cart"]:
            old = request.session["cart"]
            request.session["cart"] = old + "," + barcode_ean13_no_check_bit
        else:
            request.session["cart"] = barcode_ean13_no_check_bit

    else:
        messages.error(request, "Kein valider Barcode")

    return redirect(request.META["HTTP_REFERER"])
