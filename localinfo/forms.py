from django.forms import ModelForm
from django.forms.widgets import TextInput

from localinfo.models import DayDescription


class DayDescriptionForm(ModelForm):
    class Meta:
        model = DayDescription
        widgets = {
                   'color': TextInput(attrs={'type': 'color'}),
                   }
        fields = ('color', 'description')

