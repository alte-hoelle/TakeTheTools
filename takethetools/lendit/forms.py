from bootstrap_datepicker_plus import DatePickerInput

from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Field, Fieldset

from .models import Purpose, Tool, CustomImage

class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=100,label='Nutzerin')
    password = forms.CharField(widget=forms.PasswordInput, max_length=100,label='Password')
    email = forms.CharField(max_length=100,label='Mail')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-row p-3 mt-4 mb-4 border bg-light form-inline'
        self.helper.field_class = 'col-auto'

        self.helper.layout = Layout(
            Field('username', placeholder='Nutzerin'),
            Field('password', placeholder='Password'),
            Field('email', placeholder='Mail'),
        )
        self.helper.form_method = 'post'
        self.helper.form_action = 'adduser'
        self.helper.form_show_labels = False
        self.helper.add_input(Submit('submit', 'Registrieren'))


class UserRegistrationFormChip(forms.Form):
    username = forms.CharField(max_length=100, label='Nutzerin')
    email = forms.CharField(max_length=100, label='Mail')
    chip_id = forms.CharField(max_length=10, label='Chip ID')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-row p-3 mt-4 mb-4 border bg-light form-inline'
        self.helper.field_class = 'col-auto'

        self.helper.layout = Layout(
            Field('username', placeholder='Nutzerin'),
            Field('email', placeholder='Mail'),
            Field('chip_id', placeholder='Chip ID'),
        )
        self.helper.form_method = 'post'
        self.helper.form_action = 'adduser'
        self.helper.form_show_labels = False
        self.helper.add_input(Submit('submit', 'Mit Chip registrieren'))


class AddItemToCartIDForm(forms.Form):
    item_id = forms.CharField(label='Werkzeug-ID',
                              strip=True,
                              widget=forms.TextInput(attrs={
                                                            'placeholder': 'Werkzeug-ID',
                                                            'class': 'form-control',
                                                            'autofocus': True
                                                            })
                              )


class CheckoutForm(forms.Form):
    expected_end = forms.DateField(label="Rückgabe am", input_formats=['%d/%m/%Y'],
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
    link = forms.URLField(label="Bild URL", required=False)

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
        if image_link not in ("", None):

            im = CustomImage()
            im.supplied_source = cleaned_data.get('link')
            f_name = cleaned_data.get('name') + '_' + \
                cleaned_data.get('brand') + '_' + \
                cleaned_data.get('model') + '_' + \
                cleaned_data.get('barcode_ean13_no_check_bit') + ".jpg"

            if not im.save(cleaned_data.get('link'), f_name):
                raise ValidationError('Image from given Link not downloadable or not an Image.')

            cleaned_data['img'] = im
        else:
            try:
                cleaned_data['img'] = CustomImage.objects.get(default=True) # unsafe, there could be multiple
            except Exception:
                raise ValidationError('No default image exists, either mark one as default or add a picture URL')


class ExportSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tools = Tool.objects.all()
        for tool in tools:
            self.fields[str(tool.id)] = forms.IntegerField(label = str(tool), initial=0, required=True, min_value=0)
