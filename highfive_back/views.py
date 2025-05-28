import json
from typing import Dict

import requests
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class AdminView(View):
    BASE_URL = 'http://admin:8003/admin'

    def post(self, request):
        # 1) 요청 body를 JSON으로 파싱
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # 2) 외부 Admin 서비스에 POST 요청
        try:
            resp = requests.post(self.BASE_URL, json=payload, timeout=100)
        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"Admin 로그인 요청 실패: {e}"},
                status=502
            )

        # 3) 응답을 JSON으로 파싱 시도
        try:
            data = resp.json()
            # 리스트인지 판별하여 safe 플래그 설정
            is_list = isinstance(data, list)
            return JsonResponse(data, safe=not is_list, status=resp.status_code)
        except ValueError:
            # JSON이 아니면 바이트/텍스트 그대로 반환
            return HttpResponse(
                resp.content,
                status=resp.status_code,
                content_type=resp.headers.get("Content-Type", "application/octet-stream")
            )


@method_decorator(csrf_exempt, name='dispatch')
class LikeProxyView(View):
    BASE_URL = 'http://product:8001/product'

    def post(self, request, id):
        url = f'{self.BASE_URL}/{id}/like'
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        resp = requests.post(url, json=payload)
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

    def delete(self, request, id, user_id):
        if not id:
            return JsonResponse({"error": "Product id required"}, status=400)
        url = f"{self.BASE_URL}/{id}/like/{user_id}"
        resp = requests.delete(url)
        if resp.status_code == 204:
            return HttpResponse(status=204)
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def get(self, request, user_id):
        # 1) URL 결정: 단일 조회 vs. 전체 리스트

        url = f"{self.BASE_URL}/like/count/{user_id}"

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


# CSRF exempt for internal microservice proxy
@method_decorator(csrf_exempt, name="dispatch")
class ProductProxyView(View):
    BASE_URL = "http://product:8001/product"

    def get(self, request, id=None):
        # 1) URL 결정: 단일 조회 vs. 전체 리스트
        if id is not None:
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


@method_decorator(csrf_exempt, name='dispatch')
class BrandLikeProxyView(View):
    BASE_URL = 'http://product:8001/brand'

    def post(self, request, id):
        """브랜드 좋아요"""
        url = f'{self.BASE_URL}/{id}/like'
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        resp = requests.post(url, json=payload)
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

    def delete(self, request, id, user_id):
        """브랜드 좋아요 취소"""
        if not id:
            return JsonResponse({"error": "Brand id required"}, status=400)
        url = f'{self.BASE_URL}/{id}/like/{user_id}'
        resp = requests.delete(url)
        if resp.status_code in (200, 204):
            return HttpResponse(status=resp.status_code)
        # JSON 오류날 수도 있으니 safe=False
        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def get(self, request, user_id):
        """사용자가 좋아요한 브랜드 리스트 조회"""
        # QueryDict → dict
        params = request.GET.dict()
        url = f'{self.BASE_URL}/like/count/{user_id}'
        try:
            resp = requests.get(url, params=params, timeout=100)
            resp.raise_for_status()
        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"브랜드 서비스 요청 실패: {e}"},
                status=502
            )
        try:
            payload = resp.json()
        except ValueError:
            return HttpResponse(
                resp.content,
                status=resp.status_code,
                content_type=resp.headers.get("Content-Type", "application/octet-stream")
            )
        is_list = isinstance(payload, list)
        return JsonResponse(payload, safe=not is_list, status=resp.status_code)


@method_decorator(csrf_exempt, name="dispatch")
class OrderProxyView(View):
    BASE_URL = "http://order:8004/order"

    def get(self, request, user_id=None):
        # 1) URL 결정
        url = f"{self.BASE_URL}/{user_id}" if user_id else self.BASE_URL
        resp = requests.get(url, params=request.GET)

        # 2) HTTP 오류 체크
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # 하위 서비스가 4xx/5xx를 보내면 그대로 전달
            return JsonResponse(
                {"error": str(e)}, status=resp.status_code
            )

        # 3) 빈 바디(204 등) 처리
        if not resp.text:
            return JsonResponse({}, status=resp.status_code)

        # 4) Content-Type 검사
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            # JSON 아닌 경우
            return JsonResponse(
                {"error": f"Invalid Content-Type: {content_type}"},
                status=502
            )

        # 5) JSON 파싱
        try:
            data = resp.json()
        except ValueError:
            # 파싱 실패 시 빈 JSON 객체로 대응
            return JsonResponse({}, status=502)

        # 6) 리스트인지 판단해서 safe 파라미터 결정
        return JsonResponse(data, safe=False, status=resp.status_code)

    def post(self, request, *args, **kwargs):
        # is_from_cart 경로 파라미터가 들어올 수도 있음
        url = f"{self.BASE_URL}"
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        resp = requests.post(url, json=payload)
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

    def post(self, request, user_id):
        # 1) load the raw JSON from the incoming Django request
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)

        # 2) forward as JSON to your cart service
        resp = requests.post(
            f"http://cart:8002/cart/{user_id}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        return JsonResponse(resp.json(), status=resp.status_code)

    def get(self, request, user_id=None):
        if not user_id:
            return JsonResponse({"error": "user_id required"}, status=400)
        url = f"{self.BASE_URL}/{user_id}"
        resp = requests.get(
            url=url,
            json=request.GET.dict(),
            params=request.GET,
            timeout=10
        )

        return JsonResponse(resp.json(), safe=False, status=resp.status_code)

    def put(self, request, user_id=None, product_id=None):
        # 1) 필수 파라미터 체크
        if not user_id or not product_id:
            return JsonResponse(
                {"error": "user_id and product_id required"},
                status=400
            )

        # 2) JSON 파싱 ({"quantity": N})
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # 3) Cart 서비스에 PUT 요청
        url = f"{self.BASE_URL}/{user_id}/{product_id}"
        try:
            resp = requests.put(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"Cart service error: {e}"},
                status=502
            )

        # 4) FastAPI가 200 OK로 전체 카트를 반환하면 그대로 JSON 리턴
        if resp.status_code == 200:
            try:
                data = resp.json()  # ← 반드시 호출
            except ValueError:
                return HttpResponse(status=502)
            return JsonResponse(data, safe=False, status=200)

        # 5) 422 등 에러 바디가 있으면 그대로 리턴
        try:
            data = resp.json()
            return JsonResponse(data, safe=False, status=resp.status_code)
        except ValueError:
            return HttpResponse(status=resp.status_code)

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


@method_decorator(csrf_exempt, name="dispatch")
class RecommendProxyView(View):
    BASE_URL = "http://recommend:8007/recommend"

    def get(self, request, user_id):
        # 1) 내부 recommend 서비스 호출 (/recommend/{user_id}?top_n=n)
        try:
            resp = requests.get(
                f"{self.BASE_URL}/{user_id}",
                params=request.GET.dict(),
                timeout=10
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            return JsonResponse(
                {"error": f"Recommend 서비스 요청 실패: {e}"},
                status=502
            )

        # 2) JSON 파싱
        try:
            payload = resp.json()
        except ValueError:
            # JSON이 아닐 경우 원본 바이트/텍스트 그대로 반환
            return HttpResponse(
                resp.content,
                status=resp.status_code,
                content_type=resp.headers.get("Content-Type", "application/octet-stream")
            )

        # 3) JsonResponse 생성 (dict이므로 safe=True)
        return JsonResponse(payload, safe=True, status=resp.status_code)


class AlertProxyView(View):
    BASE_URL = "http://alert:8005/alert"  # alert 서비스 호스트:포트/경로

    def post(self, request):
        # 1) 입력 JSON 파싱
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)

        # 2) alert 서비스에 POST 요청
        try:
            resp = requests.post(
                self.BASE_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
        except requests.RequestException as e:
            return JsonResponse({"error": f"Alert service error: {e}"}, status=502)

        # 3) 응답 JSON 파싱
        try:
            data = resp.json()
        except ValueError:
            return HttpResponse(status=502)

        return JsonResponse(data,
                            safe=isinstance(data, list),
                            status=resp.status_code)

    def get(self, request, alert_id=None):
        # 경로 구성
        url = f"{self.BASE_URL}/{alert_id}" if alert_id else self.BASE_URL

        # alert 서비스 GET 요청
        try:
            resp = requests.get(url, params=request.GET, timeout=5)
        except requests.RequestException as e:
            return JsonResponse({"error": f"Alert service error: {e}"}, status=502)

        # JSON 파싱
        try:
            data = resp.json()
        except ValueError:
            return HttpResponse(status=502)

        return JsonResponse(data,
                            safe=isinstance(data, list),
                            status=resp.status_code)

    def put(self, request, alert_id=None):
        # alert_id 필수 체크
        if not alert_id:
            return JsonResponse({"error": "alert_id required"}, status=400)

        # JSON 파싱
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # alert 서비스에 PUT 요청
        try:
            resp = requests.put(
                f"{self.BASE_URL}/{alert_id}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
        except requests.RequestException as e:
            return JsonResponse({"error": f"Alert service error: {e}"}, status=502)

        # JSON 파싱
        try:
            data = resp.json()
        except ValueError:
            return HttpResponse(status=502)

        return JsonResponse(data,
                            safe=isinstance(data, list),
                            status=resp.status_code)

    def delete(self, request, alert_id=None):
        # alert_id 필수 체크
        if not alert_id:
            return JsonResponse({"error": "alert_id required"}, status=400)

        # DELETE 요청
        try:
            resp = requests.delete(f"{self.BASE_URL}/{alert_id}", timeout=5)
        except requests.RequestException as e:
            return JsonResponse({"error": f"Alert service error: {e}"}, status=502)

        # 204 No Content
        if resp.status_code in (200, 204):
            return HttpResponse(status=resp.status_code)

        # 에러 바디 JSON 파싱
        try:
            data = resp.json()
            return JsonResponse(data, safe=False, status=resp.status_code)
        except ValueError:
            return HttpResponse(status=resp.status_code)

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
