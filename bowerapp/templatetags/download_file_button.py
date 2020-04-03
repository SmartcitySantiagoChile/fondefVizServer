# -*- coding: utf-8 -*-

from django import template
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse

register = template.Library()

@register.simple_tag
def download_file_button(stepId, scene, disabled = ""):
    url = reverse("scene:downloadStepFile", kwargs={"stepId":stepId, "sceneId":scene.id})

    if stepId == 1:
        timeStamp = scene.timeStampStep1File
    elif stepId == 3:
        timeStamp = scene.timeStampStep3File
    elif stepId == 5:
        timeStamp = scene.timeStampStep5File
    elif stepId == 6:
        timeStamp = scene.timeStampStep6File
    else:
        timeStamp = None

    if timeStamp is None:
        timeStamp = ""
        disabled = "disabled"
    else:
        timeStamp = timezone.localtime(timeStamp).strftime("%Y-%m-%d %H:%M:%S")

    field = """
     <a href="{}" class="btn btn-success btn-lg btn-block {}">
       <i class="fa fa-file-excel-o"></i> {}
       (<span id="timestamp1">{}</span>)
     </a>
    """
    buttonMessage = "Descargar ultimo archivo subido"
    return format_html(field, url, disabled, buttonMessage, timeStamp)
