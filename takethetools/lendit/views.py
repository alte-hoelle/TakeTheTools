import string
import random

from datetime import datetime
from django_tables2 import SingleTableView, SingleTableMixin

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django_filters.views import FilterView

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from .forms import (
    ExportSelectionForm,
    CheckoutForm,
    CheckinForm,
    AddItemToCartIDForm,
    UserRegistrationForm,
    ToolRegistrationForm,
    UserRegistrationFormChip,
)
from .models import Tool, Lendlog, Purpose, CustomUser
from .tables import ToolTable, UserTable
from .filters import ToolFilter
from .barcode_gen import Sheet


class ToolList(LoginRequiredMixin, PermissionRequiredMixin, SingleTableMixin, FilterView):
    permission_required = "lendit.view_tool"
    template_name = "tool_list.html"
    model = Tool
    queryset = Tool.objects.all()
    table_class = ToolTable
    filterset_class = ToolFilter


class UserList(LoginRequiredMixin, PermissionRequiredMixin, SingleTableView):
    permission_required = 'lendit.view_customuser'
    template_name = "user_list.html"
    table_class = UserTable

    def get_queryset(self, *args, **kwargs):
        User = get_user_model()
        return User.objects.all()


class Home(TemplateView):
    template_name = "home.html"


class ToolCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'lendit.add_tool'
    model = Tool
    form_class = ToolRegistrationForm
    success_url = reverse_lazy('tools')
    template_name = 'tool_reg.html'


@login_required
def Overview(request):
    #permission_required = 'lendit.view_lendlog'
    # make this a CBV first
    active = Lendlog.objects.filter(status=1)
    inactive = Lendlog.objects.filter(status=0)

    context = {"active": active, "returned": inactive}
    return render(request, "stats.html", context)


@login_required
def registerUser(request):
    context = {"form": UserRegistrationForm, "form_chip": UserRegistrationFormChip}
    return render(request, "user_reg.html", context)


@login_required
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


@login_required
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

@login_required
def Checkout(request):

    form = CheckoutForm(request.POST)
    form_in = CheckinForm(request.POST)

    ids = request.session["cart"]
    if not ids:

        return redirect("cart")

    if "lend" in request.POST:
        #print(form.cleaned_data["lendby"])
        if form.is_valid():

            idlist = ids.split(",")
            for id in idlist:
                ok, msg = lendTool(
                        barcode=id,
                        purpose=form.cleaned_data["purpose"],
                        end=form.cleaned_data["expected_end"],
                        lender= make_password(form.cleaned_data["lendby"], settings.CHIP_SALT)
                )

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
                if str(lend.tool.barcode_ean13_no_check_bit) in idlist:
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

@login_required
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

@login_required
def clearbasket(request):
    del request.session["cart"]
    return redirect("cart")

@login_required
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

@login_required
def exportBarcodes(request):

    context = {"form": ExportSelectionForm}

    return render(request, "export_barcodes.html", context)


@login_required
def exportBarcodesPDF(request):

    form = ExportSelectionForm()
    export_sheet = Sheet()

    for field in form.get_interest_fields():
        export_sheet.add_tool(int(field.name))

    export_sheet.list()
    export_sheet.export()
    return redirect("export")


@login_required
def test_view(request, barcode_ean13_no_check_bit='999999999999'):

    if Tool.objects.filter(barcode_ean13_no_check_bit=barcode_ean13_no_check_bit).exists():

        if request.session["cart"]:
            old = request.session["cart"]
            request.session["cart"] = old + "," + barcode_ean13_no_check_bit
        else:
            request.session["cart"] = barcode_ean13_no_check_bit

    else:
        messages.error(request, "Kein valider Barcode")

    return redirect(request.META['HTTP_REFERER'])


def logout_request(request):
    logout(request)
    messages.info(request, "Du hast dich erfolgreich ausgeloggt")
    return redirect("login")


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request = request, template_name="login.html", context={"form":form})