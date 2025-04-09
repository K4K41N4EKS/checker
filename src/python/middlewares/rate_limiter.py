import time
from fastapi import status
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.python.utils.logger_utils import get_logger

RATE_LIMIT_STORE = {}
VIOLATION_TRACKER = {}
BLOCKED_CLIENTS = {}

MAX_REQUESTS_PER_MINUTE = 100
MAX_VIOLATIONS = 4
BLOCK_DURATION = 600
EXEMPT_PATHS = ["/create_user"]

logger = get_logger("middleware.rate_limiter")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        now = int(time.time())

        if any(path.startswith(exempt) for exempt in EXEMPT_PATHS):
            return await call_next(request)

        identifier = self._get_identifier(request)
        ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")

        # Блокировка
        if identifier in BLOCKED_CLIENTS:
            block_time = BLOCKED_CLIENTS[identifier]
            if now < block_time:
                logger.warning(f"[BLOCKED] {identifier} | IP: {ip} | User-Agent: {user_agent} | До: {block_time}")
                return Response(
                    content="Вы временно заблокированы из-за превышения лимита.",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS
                )
            else:
                del BLOCKED_CLIENTS[identifier]
                VIOLATION_TRACKER[identifier] = 0
                logger.info(f"[UNBLOCKED] {identifier} | IP: {ip}")

        # Подсчет запросов в текущем окне
        window = now // 60
        key = f"{identifier}:{window}"
        RATE_LIMIT_STORE[key] = RATE_LIMIT_STORE.get(key, 0) + 1

        if RATE_LIMIT_STORE[key] > MAX_REQUESTS_PER_MINUTE:
            VIOLATION_TRACKER[identifier] = VIOLATION_TRACKER.get(identifier, 0) + 1
            logger.warning(f"[RATE LIMIT EXCEEDED] {identifier} | Нарушение #{VIOLATION_TRACKER[identifier]} | IP: {ip} | User-Agent: {user_agent}")

            if VIOLATION_TRACKER[identifier] >= MAX_VIOLATIONS:
                BLOCKED_CLIENTS[identifier] = now + BLOCK_DURATION
                logger.error(f"[BLOCKED] {identifier} | IP: {ip} | Заблокирован на {BLOCK_DURATION} сек.")
                return Response(
                    content="Слишком много нарушений. Вы заблокированы на 10 минут.",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS
                )

            return Response(
                content="Превышен лимит запросов. Попробуйте позже.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        return await call_next(request)

    def _get_identifier(self, request: Request) -> str:
        """
        Возвращает идентификатор: access_token (если есть), иначе IP.
        """
        auth = request.headers.get("authorization")
        if auth and auth.startswith("Bearer "):
            return auth.split(" ")[1][:25]  # усечённый токен
        return request.client.host
