from django.forms import ModelForm
from django.forms.widgets import TextInput, HiddenInput
from django.template.loader import get_template

from localinfo.models import DayDescription, FAQ


class TrixEditorWidget(TextInput):
    template_name = "localinfo/trix_editor.html"

    class Media:
        css = {'all': ('components/trix/dist/trix.css',)}
        js = ('components/trix/dist/trix.js', '')

    def __init__(self, attrs=None, *args, **kwargs):
        attrs = attrs or {}
        default_options = {}
        options = kwargs.get('options', {})
        default_options.update(options)
        for key, val in list(default_options.items()):
            attrs['data-' + key] = val

        super(TrixEditorWidget, self).__init__(attrs)


class DayDescriptionForm(ModelForm):
    class Meta:
        model = DayDescription
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }
        fields = ('color', 'description')


class FAQForm(ModelForm):
    class Meta:
        model = FAQ
        widgets = {
            'answer': TrixEditorWidget
        }
        fields = ('question', 'answer', 'category')
