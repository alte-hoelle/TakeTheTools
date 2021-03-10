from django.shortcuts import render, redirect
from .models import Tool, Lendlog, Purpose
from .forms import CheckoutForm, CheckinForm, AddItemToCartIDForm, UserRegistrationForm, ToolRegistrationForm, UserRegistrationFormChip
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.core.cache import cache

import wget
import os
import string
import random
from barcode.writer import ImageWriter
from PIL import Image
from barcode import EAN13
from datetime import datetime

def Tools(request):

    obj = Tool.objects.all()
    context = {
        "tooldata":obj
    }
    return render(request, 'items.html', context)

def Users(request):
    User = get_user_model()
    obj = User.objects.all()
    context = {
        "userdata":obj
    }
    return render(request, 'users.html', context)
def Home(request):

    context = {
        "name": "stoerte"
    }
    return render(request, 'home.html', context)

def Registeruser(request):
    context = {
        "list": ["fuck", "this", "stupid", "tryhard", "bullshit"]
    }
    return render(request, 'users.html', context)

def Overview(request):
    active = Lendlog.objects.filter(status = 1)
    inactive = Lendlog.objects.filter(status = 0)

    context = {
        "active":active,
        "returned":inactive
    }
    return render(request, 'stats.html', context)

def registerUser(request):
    context = {
        "form":UserRegistrationForm,
        "form_chip":UserRegistrationFormChip
    }
    return render(request, 'user_reg.html', context)

def addUser(request):
    form = UserRegistrationForm(request.POST)
    form_chip = UserRegistrationFormChip(request.POST)

    if form.is_valid():
        User = get_user_model()

        newuser = User(
            id = random.randint(1000000, 9999999),
            password = "",
            last_login = datetime.now(),
            is_superuser = 0,
            username = form.cleaned_data["username"],
            last_name = "",
            email = form.cleaned_data["email"],
            is_staff = 0,
            is_active = 1,
            date_joined = datetime.now(),
            first_name = ""
        )
        newuser.set_password(form.cleaned_data["password"])
        newuser.save()
        return redirect('users')
    elif form_chip.is_valid():
        User = get_user_model()
        newuser = User(
            id = int("1" + form_chip.cleaned_data["chip_id"]),
            password="",
            last_login=datetime.now(),
            is_superuser=0,
            username=form_chip.cleaned_data["username"],
            last_name="",
            email=form_chip.cleaned_data["email"],
            is_staff=0,
            is_active=1,
            date_joined=datetime.now(),
            first_name=""
        )

        output_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        newuser.set_password(output_string)
        newuser.save()
        return redirect('users')
    else:
        return redirect('index')

def registerTool(request):
    context = {
        "form":ToolRegistrationForm
    }
    return render(request, 'tool_reg.html', context)

def addTool(request):
    form = ToolRegistrationForm(request.POST)

    if form.is_valid():
        User = get_user_model()
        print(form.cleaned_data["owner"])
        sub_owner = User.objects.get(username = form.cleaned_data["owner"])
        if form.cleaned_data["id"] in("", None):
            toolid = int('99'+str(random.randint(1000000000,9999999999)))
        else:
            toolid = form.cleaned_data["id"]

        path = os.path.abspath(os.path.dirname(__file__))
        path = path.split("/")

        path.pop(-1)
        path_new = '/'.join([str(item) for item in path])

        name = ""
        if not form.cleaned_data["image_link"]:
            name = "default.png"
        else:
            image_filename = wget.download(form.cleaned_data["image_link"])
            name = str(toolid) + ".jpg"
            im = Image.open(image_filename)
            im.thumbnail((60, 60), Image.ANTIALIAS)

            os.system("rm " + image_filename)
            impath = os.path.join(path_new, "static", "img", "tool_icons", name)
            print(path)
            print(path_new)
            print(impath)
            print(os.path.join(settings.TOOL_IMAGE_FOLDER, name))
            im.save(impath, "JPEG")

        with open('somefile.jpeg', 'wb') as f:
            EAN13(str(toolid), writer=ImageWriter()).write(f)

        toolregister = Tool(
            id = toolid,
            name = form.cleaned_data["name"],
            brand = form.cleaned_data["brand"],
            price = form.cleaned_data["price"],
            description = form.cleaned_data["description"],
            owner = sub_owner,
            available_amount = form.cleaned_data["available_amount"],
            sec_class = form.cleaned_data["sec_class"],
            trust_class = form.cleaned_data["trust_class"],
            img_local_link = os.path.join(settings.TOOL_IMAGE_FOLDER, name),
            buy_date = form.cleaned_data["buy_date"]
            )

        toolregister.save()
        return redirect('tools')

def lendTool(id=0, end=datetime.today(), lender=0, purpose="Verein"):

    current_tool = Tool.objects.get(id=int(id))
    purpose = Purpose.objects.get(name=purpose)
    try:
        user = get_user_model().objects.get(id=int(lender))
    except Exception as e:
        print(e, lender, current_tool)
        return False, "User was not found"

    newlog = Lendlog(
        tool=current_tool,
        from_date=datetime.today(),
        expected_end_date=end,
        end_date=None,
        status=1,
        lend_by=user,
        returned_by=None,
        purpose=purpose
    )

    newlog.save()

    current_tool.present_amount = current_tool.present_amount - 1
    current_tool.save()
    return True, ""

def Checkout(request):

    form = CheckoutForm(request.POST)
    form_in = CheckinForm(request.POST)

    ids = cache.get("cart")
    if not ids:

        return redirect('cart')

    if 'lend' in request.POST:
        if form.is_valid():

            idlist = ids.split(",")
            for id in idlist:

                ok, msg = lendTool(id=id,
                         purpose=form.cleaned_data["purpose"],
                         end=form.cleaned_data["expected_end"],
                         lender="1" + form.cleaned_data["lendby"])
                print(ok, msg)
                if not ok:
                    messages.error(request, msg)
                    return redirect('cart')

            clearbasket(request)
            messages.success(request, "Voll ausgeliehen! Geilo!")

    elif 'return' in request.POST:

        if form_in.is_valid():
            try:
                returner = get_user_model().objects.get(id=int("1" + form_in.cleaned_data["returned_by"]))
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
                    idlist.remove(str(lend.tool.id))
                    return_cnt += 1
                    lend.save()
            if not idlist:
                cache.set("cart", "")
                messages.success(request, "Alle " + str(return_cnt) + " Werkzeuge zurück gegeben")
            else:
                cache.set("cart",','.join([str(item) for item in idlist]))
                messages.warning(request, str(return_cnt) + " Werkzeuge zurück gegeben, einige nicht, hast du sie geliehen?")
    else:
        pass
    return redirect('cart')

@cache_page(60 * 30)
def addToCart(request):

    form = AddItemToCartIDForm(request.POST or None)
    if "add" in request.POST:
        if form.is_valid():

            if Tool.objects.filter(id = int(form.cleaned_data["item_id"])).exists():

                if cache.get("cart"):
                    old = cache.get("cart")
                    cache.set("cart", old + "," + form.cleaned_data["item_id"])
                else:
                    cache.set("cart", form.cleaned_data["item_id"])

            else:
                pass
    elif 'clear' in request.POST:
        cache.delete("cart")
    return redirect('cart')

def clearbasket(request):
    cache.delete("cart")
    return redirect('cart')

def Cart(request):

    display_dict = {}
    if cache.get("cart"):
        display_cart = cache.get("cart").split(",")

        if display_cart:
            i = 1
            for id in display_cart:
                if id:
                    temp_tool = Tool.objects.get(id = int(id))
                    display_dict[i] = [temp_tool.name, temp_tool.brand, temp_tool.description, temp_tool.owner.username, temp_tool.img_local_link]
                    i+=1

    context = {}
    context["add_to_cart"] = AddItemToCartIDForm
    context["checkout_form"] = CheckoutForm
    context["checkin_form"] = CheckinForm

    if display_dict :
        context["cart"] = display_dict
    else:
        context["cart"] = False

    return render(request, 'cart.html', context)