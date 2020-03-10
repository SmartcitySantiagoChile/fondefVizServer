import csv
import os

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from localinfo.helper import get_all_faqs, search_faq
from localinfo.models import CustomRoute


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
        if csv_file and len(csv_file.read()) != 0:
            f = open(csv_file.name, 'r')
            reader = csv.reader(f)
            for row in reader:
                if row[1].strip():
                    CustomRoute.objects.update_or_create(
                        auth_route_code=row[0], defaults={'custom_route_code': row[1]})
            return JsonResponse(data={"status": True})
        else:
            return JsonResponse(data={"error": "No existe archivo."}, status=500)
