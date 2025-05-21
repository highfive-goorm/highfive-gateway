import time
import logging

logger = logging.getLogger("user")  # settings.py 에 configure_logging 으로 붙인 핸들러를 쓸 겁니다

class RequestLoggingMiddleware:
    """
    모든 요청에 대해, 응답 직후 한 줄로 로그를 남깁니다.
    - method, path, status_code, elapsed_ms, user_id(fallback(""))
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        elapsed_ms = (time.time() - start) * 1000

        user_id = getattr(request.user, "user_id", "") if hasattr(request, "user") else ""

        # 탭(\t) 구분 메시지
        msg = (
            f"api_request\t"
            f"method={request.method}\t"
            f"path={request.path}\t"
            f"status_code={response.status_code}\t"
            f"process_time_ms={elapsed_ms:.2f}\t"
            f"user_id={user_id}"
        )
        logger.info(msg)

        return response
