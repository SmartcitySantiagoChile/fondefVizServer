import csv
from io import StringIO

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from localinfo.helper import get_all_faqs, search_faq
from localinfo.models import OPDictionary


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


class OPDictionaryCsvUploader(View):

    def post(self, request):
        csv_file = request.FILES.get('csvDictionary', False)
        if csv_file and csv_file.size != 0:
            try:
                csvf = StringIO(csv_file.read().decode())
                upload_time = timezone.now()
                reader = csv.reader(csvf, delimiter=',')
                to_update = []
                to_create = []
                for row in reader:
                    if row[1].strip():
                        try:
                            op_dict_obj = OPDictionary.objects.get(auth_route_code=row[0])
                            op_dict_obj.user_route_code = row[1]
                            op_dict_obj.op_route_code = row[2]
                            op_dict_obj.route_type = row[3]
                            op_dict_obj.updated_at = upload_time
                            to_update.append(op_dict_obj)
                        except OPDictionary.DoesNotExist:
                            to_create.append(OPDictionary(user_route_code=row[1], op_route_code=row[2],
                                                          route_type=row[3], created_at=upload_time,
                                                          updated_at=upload_time,
                                                          auth_route_code=row[0]))
                OPDictionary.objects.bulk_create(to_create)
                OPDictionary.objects.bulk_update(to_update,
                                                 ['user_route_code', 'op_route_code', 'route_type', 'updated_at'])
                return JsonResponse(data={"status": True})
            except Exception:
                return JsonResponse(data={"error": "El archivo tiene problemas en su formato."}, status=400)

        else:
            return JsonResponse(data={"error": "No existe archivo."}, status=400)
