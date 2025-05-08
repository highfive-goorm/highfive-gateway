import requests
from django.http import JsonResponse
from django.views import View


class ProductProxyView(View):
    def get(self, request):
        response = requests.get('http://localhost:8001/product/{id}')
        return JsonResponse(response.json(), safe=False)

    def post(self, request):
        response = requests.post('http://localhost:8001/product', json=request.POST)
        return JsonResponse(response.json())
