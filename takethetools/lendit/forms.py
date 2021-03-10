from django import forms
from .models import Purpose, Category
from bootstrap_datepicker_plus import DatePickerInput
from django.contrib.auth import get_user_model

class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, max_length=100)
    email = forms.CharField(max_length=100)

class UserRegistrationFormChip(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.CharField(max_length=100)
    chip_id = forms.CharField(max_length=10)

class AddItemToCartIDForm(forms.Form):
    item_id = forms.CharField(label=('Werkzeug-ID'),
    strip=True,
    widget=forms.TextInput(attrs={'placeholder': ('Werkzeug-ID'), 'class': 'form-control', 'autofocus': True})
)

class CheckoutForm(forms.Form):
    expected_end = forms.DateField(label="Rückgabe am",input_formats=['%d/%m/%Y'],
                                   widget=DatePickerInput(format='%d/%m/%Y'))

    purpose = forms.ModelChoiceField(label="Zweck", queryset=Purpose.objects.all())
    lendby = forms.CharField(label="ChipID")

class CheckinForm(forms.Form):
    returned_by = forms.CharField(label="ChipID")


class ToolRegistrationForm(forms.Form):
    id = forms.IntegerField(label="Barcode", max_value=9999999999999, required=False)
    name = forms.CharField(label="Bezeichnung", max_length=30)
    model = forms.CharField(label="Modellnummer", max_length=30, required=False)
    brand = forms.CharField(label="Marke", max_length=30, required=False)
    price = forms.IntegerField(label="Preis", required = False)
    description = forms.CharField(label="Beschreibung", max_length=200, required=False)
    owner = forms.ModelChoiceField(label="Eigentümerin", queryset=get_user_model().objects.all())
    available_amount = forms.IntegerField(label="Verfügbare Menge")
    sec_class = forms.IntegerField(label="Sicherheitsklasse")
    trust_class = forms.IntegerField(label="Vertrauensklasse")
    buy_date = forms.DateField(label="Gakauft am",input_formats=['%d/%m/%Y'],
                                   widget=DatePickerInput(format='%d/%m/%Y'))
    category = forms.ModelChoiceField(label="Kategorie", queryset=Category.objects.all())
    image_link = forms.URLField(label="Bild URL", max_length=300,required=False)
    # trust class is whajt