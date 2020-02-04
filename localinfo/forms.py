from django.forms import ModelForm
from django.forms.widgets import TextInput, HiddenInput
from django.template.loader import get_template

from localinfo.models import DayDescription, FAQ


class TrixEditorWidget(TextInput):
    template_name = "profile/trix_editor.html"
    #TRIX_HIDE_TOOLBAR = 'data-trix-toolbar-hide'
    #TRIX_ENABLE = 'data-trix-contenteditable'

    class Media:
        css = {'all': ('components/trix/dist/trix.css',)}
        js = ('components/trix/dist/trix.js', '')

    def __init__(self, attrs=None, *args, **kwargs):
        attrs = attrs or {}
        default_options = {}
        options = kwargs.get('options', {})
        default_options.update(options)
        for key, val in default_options.items():
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
        fields = ('title', 'question', 'answer')

    # def __init__(self, *args, **kwargs):
    #     read_only = kwargs.pop('read_only', True)
    #     super(FAQSForm, self).__init__(*args, **kwargs)
    #     instance = getattr(self, 'instance', None)
    #     if instance and (instance.sent and read_only):
    #         for field_name in self.fields:
    #             self.fields[field_name].disabled = True
    #             if isinstance(self.fields[field_name].widget, TrixEditorWidget):
    #                 self.fields[field_name].widget.attrs[TrixEditorWidget.TRIX_HIDE_TOOLBAR] = 'true'
    #                 self.fields[field_name].widget.attrs[TrixEditorWidget.TRIX_ENABLE] = 'false'
    #
    #
