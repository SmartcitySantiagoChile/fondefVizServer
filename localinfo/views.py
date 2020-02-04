from django.http import JsonResponse
from django.views.generic import View


class FaqImgUploader(View):

    def get(self, request):
        return JsonResponse({})

    def post(self, request):
        print(request.POST)
        return JsonResponse({})
