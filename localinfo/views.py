from django.core.files.storage import FileSystemStorage
from django.core.serializers import json
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


class FaqImgUploader(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FaqImgUploader, self).dispatch(request, *args, **kwargs)

    def process_request(self, request, params):
        print (request.FILES)
        file = request.FILES['file']
        url_to_save = 'static/faq'
        path_to_save = 'faq'
        file_storage = FileSystemStorage(url_to_save)
        print(file.name)
        file_storage.save(file.name, file)
        return JsonResponse(data={"url": path_to_save, "name": file.name})

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST)
