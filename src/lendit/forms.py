from datetime import datetime
from typing import Any, Dict

from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError

from .models import CustomImage, Note, Purpose, Tool


class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, label="Nutzerin")
    password = forms.CharField(
        widget=forms.PasswordInput, max_length=100, label="Password"
    )
    email = forms.CharField(max_length=100, label="Mail")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-row p-3 mt-4 mb-4 border bg-light form-inline"
        self.helper.field_class = "col-auto"

        self.helper.layout = Layout(
            Field("username", placeholder="Nutzerin"),
            Field("password", placeholder="Password"),
            Field("email", placeholder="Mail"),
        )
        self.helper.form_method = "post"
        self.helper.form_action = "adduser"
        self.helper.form_show_labels = False
        self.helper.add_input(Submit("submit", "Registrieren"))


class UserRegistrationFormChip(forms.Form):
    username = forms.CharField(max_length=100, label="Nutzerin")
    email = forms.CharField(max_length=100, label="Mail")
    chip_id = forms.CharField(max_length=10, label="Chip ID")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-row p-3 mt-4 mb-4 border bg-light form-inline"
        self.helper.field_class = "col-auto"

        self.helper.layout = Layout(
            Field("username", placeholder="Nutzerin"),
            Field("email", placeholder="Mail"),
            Field("chip_id", placeholder="Chip ID"),
        )
        self.helper.form_method = "post"
        self.helper.form_action = "adduser"
        self.helper.form_show_labels = False
        self.helper.add_input(Submit("submit", "Mit Chip registrieren"))


class AddItemToCartIDForm(forms.Form):
    item_id = forms.CharField(
        label="Werkzeug-ID",
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Werkzeug-ID",
                "class": "form-control",
                "autofocus": True,
            }
        ),
    )


class CheckoutForm(forms.Form):
    expected_end = forms.DateField(
        label="Rückgabe am",
        input_formats=["%d/%m/%Y"],
        widget=DatePickerInput(format="%d/%m/%Y"),
    )

    purpose = forms.ModelChoiceField(label="Zweck", queryset=Purpose.objects.all())
    lendby = forms.CharField(label="ChipID")

    def clean(self) -> Dict[str, Any]:
        # this is not working as expected, no visible message is raised
        cleaned_data = super().clean()
        if cleaned_data["expected_end"] < datetime.today().date():
            raise forms.ValidationError("Rückgabedatum vor Ausleihdatum")
        return cleaned_data


class CheckinForm(forms.Form):
    returned_by = forms.CharField(label="ChipID")


class ToolRegistrationForm(forms.ModelForm):  # type: ignore
    """
    This form is used to register new tools. If everything else is clean,
    image from the image-url (if any) is downloaded and saved. If any error
    occurs during this step, a ValidationError is raised.
    """

    link = forms.URLField(label="Bild URL", required=False)

    class Meta:
        model = Tool
        fields = (
            "name",
            "model",
            "brand",
            "price",
            "description",
            "owner",
            "available_amount",
            #''present_amount',
            "sec_class",
            "trust_class",
            "buy_date",
            "category",
            "barcode_ean13_no_check_bit",
            "img",
        )
        widgets = {"buy_date": DatePickerInput(format="%Y-%m-%d")}
        labels = {
            "name": "Bezeichnung",
            "model": "Modellnummer",
            "brand": "Marke",
            "price": "Kaufpreis",
            "description": "Kommentar",
            "owner": "Eigentümerin",
            "available_amount": "Verfügbare Menge",
            "sec_class": "Sicherheitsklasse",
            "trust_class": "Vertrauensklasse",
            "buy_date": "Kaufdatum",
            "category": "Kategorie",
            "barcode_ean13_no_check_bit": "Barcode",
        }

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        image_link = cleaned_data.get("link")
        # cleaned_data['present_amount'] = cleaned_data['available_amount']
        if image_link not in ("", None):

            image = CustomImage()
            link = f"{cleaned_data.get('link')}"
            image.supplied_source = link
            name = cleaned_data.get("name")
            brand = cleaned_data.get("brand")
            model = cleaned_data.get("model")
            barcode = cleaned_data.get("barcode_ean13_no_check_bit")
            f_name = f"{name}_{brand}_{model}_{barcode}.jpg"

            if not image.save(link, f_name):
                raise ValidationError(
                    "Image from given Link not downloadable or not an Image."
                )

            cleaned_data["img"] = image
        else:
            try:
                cleaned_data["img"] = CustomImage.objects.get(
                    default=True
                )  # unsafe, there could be multiple
            except Exception as no_default_image:
                raise ValidationError(
                    "No default image exists, either mark one as default or add a picture URL"
                ) from no_default_image
        return cleaned_data

    def save(self, commit: bool = True) -> Tool:
        tool: Tool = super().save(commit=False)  # here the object is not commited in db
        tool.present_amount = self.cleaned_data["available_amount"]
        tool.save()
        return tool


class ExportSelectionForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        tools = Tool.objects.all()
        for tool in tools:
            self.fields[str(tool.id)] = forms.IntegerField(
                label=str(tool), initial=0, required=True, min_value=0
            )


#    def get_interest_fields(self) -> None:
#        for field_name in self.fields:
#            print(self[field_name].value)
#            yield self[field_name]


class NoteForm(forms.ModelForm):  # type: ignore
    class Meta:
        model = Note
        fields = ("title", "text", "prio", "author")

        labels = {
            "title": "Titel",
            "text": "Notiz",
            "prio": "Priorität",
            "author": "Benutzerin",
        }
