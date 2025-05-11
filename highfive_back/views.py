import requests
from django.http import JsonResponse
from django.views import View


class ProductProxyView(View):
    def get(self, request,id):
        response = requests.get(f'http://localhost:8001/product/{id}',params=id)
        return JsonResponse(response.json(), safe=False)

    def post(self, request,keyword):
        response = requests.post(f'http://localhost:8001/product/{keyword}', params=keyword)
        return JsonResponse(response.json())
