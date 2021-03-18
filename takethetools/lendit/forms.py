from bootstrap_datepicker_plus import DatePickerInput

from django import forms
from django.core.exceptions import ValidationError

from .models import Purpose, Tool, CustomImage


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


class ToolRegistrationForm(forms.ModelForm):
    """
    This form is used to register new tools. If everything else is clean,
    image from the image-url (if any) is downloaded and saved. If any error
    occurs during this step, a ValidationError is raised.
    """
    link = forms.URLField(label="Bild URL")

    class Meta:
        model = Tool
        fields = (
            'name',
            'model',
            'brand',
            'price',
            'description',
            'owner',
            'available_amount',
            'sec_class',
            'trust_class',
            'buy_date',
            'category',
            'barcode_ean13_no_check_bit',
            'img'
        )
        widgets = {
            'buy_date': DatePickerInput(format='%Y-%m-%d')
        }
        labels = {
            'name': 'Bezeichnung',
            'model': 'Modellnummer',
            'brand': 'Marke',
            'price': 'Kaufpreis',
            'description': 'Kommentar',
            'owner': 'Eigentümerin',
            'available_amount': 'Verfügbare Menge',
            'sec_class': 'Sicherheitsklasse',
            'trust_class': 'Vertrauensklasse',
            'buy_date': 'Kaufdatum',
            'category': 'Kategorie',
            'barcode_ean13_no_check_bit': 'Barcode',

        }

    def clean(self):
        cleaned_data = super().clean()
        image_link = cleaned_data.get('link')
        #tool_id = cleaned_data.get('barcode_ean13_no_check_bit')
        im = CustomImage()
        im.supplied_source = cleaned_data.get('link')
        f_name = cleaned_data.get('name') + '_' + \
                 cleaned_data.get('brand') + '_' + \
                 cleaned_data.get('model') + '_' + \
                 cleaned_data.get('barcode_ean13_no_check_bit') + ".jpg"

        if not im.save(cleaned_data.get('link'), f_name):
            raise ValidationError('Image from given Link not downloadable or not an Image.')

        cleaned_data['img'] = im
        if not image_link:
            cleaned_data['image_path'] = 'default.png'
            return cleaned_data
        else:
            pass
            #ok, name = download_scale_toolicon(tool_id, image_link)
            ##if not ok:
            #    raise ValidationError('Image from given Link not downloadable or not an Image.')


class ExportSelectionForm(forms.Form):
    def __init__(self):
        super().__init__()
        tools = Tool.objects.all()
        for tool in tools:
            self.fields[str(tool.id)] = forms.IntegerField(label = str(tool), initial=0, required=True, min_value=0)

    def get_interest_fields(self):
        for field_name in self.fields:
            print(self[field_name].value)
            yield self[field_name]


