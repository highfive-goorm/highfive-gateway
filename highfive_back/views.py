import json
import requests
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
@method_decorator(csrf_exempt, name="dispatch")
class AdminView(View):
    pass
# CSRF exempt for internal microservice proxy
@method_decorator(csrf_exempt, name="dispatch")
class ProductProxyView(View):
    BASE_URL = "http://product:8001/product"

    def get(self, request):
        # 1) 쿼리 파라미터 꺼내기
        params = request.GET.dict()
        product_id = params.pop("id", None)
        name = params.pop("name", None)

        # 2) 호출할 URL 결정
        if product_id:
            url = f"{self.BASE_URL}/{product_id}"
            query = {}  # id는 URL에 넣었으니 params 비움
        else:
            url = self.BASE_URL
            # name이 있으면 name만, 없으면 빈 dict → 전체 리스트
            query = {"name": name} if name else {}

        # 3) 외부 서비스 호출
        try:
            resp = requests.get(url, params=query, timeout=self.TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"상품 서비스 호출 실패: {e}"},
                status=502
            )

        # 4) JSON 파싱 시도
        try:
            data = resp.json()
        except ValueError:
            # JSON이 아니면 그대로 바이너리/텍스트 반환
            ct = resp.headers.get("Content-Type", "application/octet-stream")
            if "charset" not in ct.lower():
                ct += "; charset=utf-8"
            return HttpResponse(resp.content, status=resp.status_code, content_type=ct)

        # 5) JsonResponse 생성
        safe = not isinstance(data, list)
        return JsonResponse(data, safe=safe, status=resp.status_code)
    def get(self, request, id=None):
        # 1) URL 결정: 단일 조회 vs. 전체 리스트
        if id:
            url = f"{self.BASE_URL}/{id}"
        else:
            url = self.BASE_URL

        # 2) 외부 서비스 호출
        try:
            # request.GET.dict()로 QueryDict → 일반 dict 변환
            resp = requests.get(url, params=request.GET, timeout=100)
            resp.raise_for_status()
        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"상품 서비스 요청 실패: {e}"},
                status=502
            )

        # 3) JSON 파싱을 시도
        try:
            payload = resp.json()
        except ValueError:
            # JSON이 아니면 바이너리/텍스트 그대로 반환
            return HttpResponse(
                resp.content,
                status=resp.status_code,
                content_type=resp.headers.get(
                    "Content-Type",
                    "application/octet-stream"
                )
            )

        # 4) JsonResponse 생성
        #    - payload가 list면 safe=False, dict면 safe=True
        is_list = isinstance(payload, list)
        return JsonResponse(
            payload,
            safe=not is_list,
            status=resp.status_code
        )

    def post(self, request, *args, **kwargs):
        # 요청 body를 JSON으로 파싱
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        resp = requests.post(self.BASE_URL, json=payload)
        try:
            data = resp.json()
            safe = not isinstance(data, list)
            return JsonResponse(data, safe=safe, status=resp.status_code)
        except ValueError:
            return HttpResponse(
                resp.content,
                status=resp.status_code,
                content_type=resp.headers.get("Content-Type", "application/octet-stream")
            )
@method_decorator(csrf_exempt, name="dispatch")
class OrderProxyView(View):
    BASE_URL = "http://order:8004/order"

    def get(self, request, id=None):
        if id:
            url = f"{self.BASE_URL}/{id}"
            resp = requests.get(url, params=request.GET)
        else:
            url = f"{self.BASE_URL}"
            resp = requests.get(url, params=request.GET)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def post(self, request, is_from_cart=None, *args, **kwargs):
        # is_from_cart 경로 파라미터가 들어올 수도 있음
        path = f"/{is_from_cart}" if is_from_cart else ""
        url = f"{self.BASE_URL}{path}"
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        resp = requests.post(url, json=payload)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def put(self, request, id=None, *args, **kwargs):
        if not id:
            return JsonResponse({"error": "Order id required"}, status=400)
        url = f"{self.BASE_URL}/{id}"
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        resp = requests.put(url, json=data)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def delete(self, request, id=None, *args, **kwargs):
        if not id:
            return JsonResponse({"error": "Order id required"}, status=400)
        url = f"{self.BASE_URL}/{id}"
        resp = requests.delete(url)
        if resp.status_code == 204:
            return HttpResponse(status=204)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

@method_decorator(csrf_exempt, name="dispatch")
class CartProxyView(View):
    BASE_URL = "http://cart:8002/cart"

    def post(self, request, user_id=None, product_id=None):
        if not user_id:
            return JsonResponse({"error": "user_id required"}, status=400)
        path = f"/{user_id}"
        url = f"{self.BASE_URL}{path}"
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        resp = requests.post(url, json=payload)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def get(self, request, user_id=None, product_id=None):
        if not user_id:
            return JsonResponse({"error": "user_id required"}, status=400)
        path = f"/{user_id}"
        if product_id:
            path += f"/{product_id}"
        url = f"{self.BASE_URL}{path}"
        resp = requests.get(url, params=request.GET)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def put(self, request, user_id=None, product_id=None):
        if not user_id or not product_id:
            return JsonResponse({"error": "user_id and product_id required"}, status=400)
        url = f"{self.BASE_URL}/{user_id}/{product_id}"
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        resp = requests.put(url, json=data)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def delete(self, request, user_id=None, product_id=None):
        if not user_id:
            return JsonResponse({"error": "user_id required"}, status=400)
        path = f"/{user_id}"
        if product_id:
            path += f"/{product_id}"
        url = f"{self.BASE_URL}{path}"
        resp = requests.delete(url)
        if resp.status_code == 204:
            return HttpResponse(status=204)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

# urls.py 매핑 예시
# from django.urls import path
# from .views import ProductProxyView, OrderProxyView, CartProxyView
# urlpatterns = [
#     # Product
#     path('product/', ProductProxyView.as_view()),
#     path('product/<str:id>/', ProductProxyView.as_view()),
#     # Order
#     path('gateway/order/', OrderProxyView.as_view()),
#     path('gateway/order/<str:is_from_cart>/', OrderProxyView.as_view()),
#     path('gateway/order/<str:id>/', OrderProxyView.as_view()),
#     # Cart
#     path('gateway/cart/<str:user_id>/', CartProxyView.as_view()),
#     path('gateway/cart/<str:user_id>/<str:product_id>/', CartProxyView.as_view()),
# ]