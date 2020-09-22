from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from localinfo.helper import get_all_faqs, search_faq, get_valid_time_period_date, get_timeperiod_list_for_select_input, \
    upload_xlsx_op_dictionary
from localinfo.models import OPProgram


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


class OPDictionaryUploader(View):

    def post(self, request):
        csv_file = request.FILES.get('OPDictionary', False)
        op_program_id = request.POST.get('opId', -1)
        if csv_file and csv_file.size != 0:
            try:
                res = upload_xlsx_op_dictionary(csv_file, op_program_id)
                return JsonResponse(data={"updated": res['updated'], "created": res['created']})
            except ValueError as e:
                return JsonResponse(data={"error": str(e)}, status=400)
            except OPProgram.DoesNotExist:
                return JsonResponse(data={"error": "Programa de operación no válido"}, status=400)
            except Exception:
                return JsonResponse(data={"error": "Archivo en formato incorrecto"}, status=400)

        else:
            return JsonResponse(data={"error": "No existe el archivo"}, status=400)


class TimePeriod(View):

    def get(self, request):
        dates = request.GET.getlist('dates[]')
        valid, date_id = get_valid_time_period_date(dates)
        if not valid:
            return JsonResponse(data={"error": "Las fechas seleccionadas ocurren entre dos periodos distintos."},
                                status=400)
        else:
            valid_period_time = get_timeperiod_list_for_select_input(filter_id=date_id)
            return JsonResponse(data={'timePeriod': valid_period_time})
