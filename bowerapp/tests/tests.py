# -*- coding: utf-8 -*-
import mock
from django.apps import apps
from django.template import Context, Template
from django.test import SimpleTestCase
from django.test import TestCase

from bowerapp.apps import BowerappConfig
from bowerapp.templatetags.download_file_button import download_file_button
from bowerapp.templatetags.toolbar import toolbar


class BowerappConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(BowerappConfig.name, 'bowerapp')
        self.assertEqual(apps.get_app_config('bowerapp').name, 'bowerapp')


class TemplateTagTest(SimpleTestCase):

    def test_rendered_bubble_message(self):
        context = Context({})
        template_to_render = Template('{% load bubble_message %}''{% bubble_message 1 1 1  %}')
        rendered_template = template_to_render.render(context)
        expected = '<div class="alert alert-1" role="alert"><strong>1</strong>1</div>'
        self.assertInHTML(expected, rendered_template)

    def test_rendered_button_message(self):
        context = Context({})
        template_to_render = Template('{% load button %}''{% button 1 1  %}')
        rendered_template = template_to_render.render(context)
        expected = '<button id="1" class="btn btn-success btn-round btn-">1</button>'
        self.assertInHTML(expected, rendered_template)

    def test_rendered_columns_message(self):
        context = Context({})
        template_to_render = Template('{% load columns %}''{% columns 1 1 1 1 %}')
        rendered_template = template_to_render.render(context)
        expected = "<div class='col-md-1 col-sm-1 col-xs-1'>1</div>"
        self.assertInHTML(expected, rendered_template)

    @mock.patch('bowerapp.templatetags.download_file_button.reverse')
    @mock.patch('bowerapp.templatetags.download_file_button.timezone')
    def test_rendered_download_file_button(self, timezone, url):
        url.return_value = 'url'
        timezone_mock = mock.MagicMock()
        timezone.localtime.return_value = timezone_mock
        timezone_mock.strftime.return_value = '2002-07-01'
        scene = mock.MagicMock(id=1, timeStampStep1File=1, timeStampStep3File=3, timeStampStep5File=5,
                               timeStampStep6File=6)

        rendered_template = download_file_button(1, scene)
        expected = '\n     <a href="url" class="btn btn-success btn-lg btn-block ">\n' \
                   '       <i class="fa fa-file-excel-o"></i> Descargar ultimo archivo subido\n' \
                   '       (<span id="timestamp1">2002-07-01</span>)\n     </a>\n    '
        self.assertEqual(expected, rendered_template)

        rendered_template = download_file_button(3, scene)
        expected = '\n     <a href="url" class="btn btn-success btn-lg btn-block ">\n' \
                   '       <i class="fa fa-file-excel-o"></i> Descargar ultimo archivo subido\n' \
                   '       (<span id="timestamp1">2002-07-01</span>)\n     </a>\n    '
        self.assertEqual(expected, rendered_template)

        rendered_template = download_file_button(5, scene)
        expected = '\n     <a href="url" class="btn btn-success btn-lg btn-block ">\n' \
                   '       <i class="fa fa-file-excel-o"></i> Descargar ultimo archivo subido\n' \
                   '       (<span id="timestamp1">2002-07-01</span>)\n     </a>\n    '
        self.assertEqual(expected, rendered_template)

        rendered_template = download_file_button(6, scene)
        expected = '\n     <a href="url" class="btn btn-success btn-lg btn-block ">\n' \
                   '       <i class="fa fa-file-excel-o"></i> Descargar ultimo archivo subido\n' \
                   '       (<span id="timestamp1">2002-07-01</span>)\n     </a>\n    '
        self.assertEqual(expected, rendered_template)

        rendered_template = download_file_button(7, scene)
        expected = '\n     <a href="url" class="btn btn-success btn-lg btn-block disabled">\n' \
                   '       <i class="fa fa-file-excel-o"></i> Descargar ultimo archivo subido\n' \
                   '       (<span id="timestamp1"></span>)\n     </a>\n    '
        self.assertEqual(expected, rendered_template)

    def test_rendered_read_only_field(self):
        context = Context({})
        template_to_render = Template('{% load read_only_field %}''{% read_only_field 1 1 1 %}')
        rendered_template = template_to_render.render(context)
        expected = '<div class="form-horizontal form-label-left"><div class="form-group">' \
                   '<label class="control-label col-md-6 col-sm-6 col-xs-12">1</label>' \
                   '<div class="input-group"><input class="form-control" readonly="readonly" value="1" />' \
                   '<span class="input-group-addon">1</span></div></div></div>'
        self.assertInHTML(expected, rendered_template)

    def test_rendered_toolbar(self):
        rendered_template = toolbar(1, 1, 2)
        expected = '<div id="1" class="btn-toolbar" role="toolbar" data-toggle="buttons">' \
                   '<div class="btn-group">&lt;label' \
                   ' class=&quot;btn btn-default&quot;&gt;&lt;input type=&quot;radio&quot; name=&quot;groups&quot;' \
                   ' value=&quot;1&quot; checked=&quot;&quot;&gt;2&lt;/label&gt;</div></div>'
        self.assertInHTML(expected, rendered_template)
