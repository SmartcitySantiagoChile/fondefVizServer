from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from localinfo.helper import get_all_faqs, search_faq, read_csv_dict


class FaqImgUploader(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FaqImgUploader, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        file = request.FILES['file']
        url_to_save = 'media/faq'
        file_storage = FileSystemStorage(url_to_save)
        file_storage.save(file.name, file)
        return JsonResponse(data={"url": url_to_save, "name": file.name})


class FaqHTML(View):

    def get(self, request):
        template = 'localinfo/faq.html'
        search = request.GET.get('search')
        if search is None or search == "":
            faqs = {"faqs": get_all_faqs()}
        else:
            faqs = {"faqs": search_faq(search),
                    "query": search}
        return render(request, template, faqs)


class CustomRouteCsvUploader(View):

    def post(self, request):
        csv_file = request.FILES.get('csvDictionary', False)
        if csv_file is not False:
            status = read_csv_dict(csv_file)
        else:
            status = "No existe archivo."
        if status == True:
            return JsonResponse(data={"status": status})
        else:
            return JsonResponse(data={"error": status}, status=500)
