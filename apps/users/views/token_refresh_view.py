from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta

ACCESS_COOKIE_NAME = getattr(settings, "ACCESS_COOKIE_NAME", "access_token")
REFRESH_COOKIE_NAME = getattr(settings, "REFRESH_COOKIE_NAME", "refresh_token")

COOKIE_SECURE = getattr(settings, "COOKIE_SECURE", not getattr(settings, "DEBUG", False))
COOKIE_SAMESITE = getattr(settings, "COOKIE_SAMESITE", "Lax")
COOKIE_HTTPONLY = getattr(settings, "COOKIE_HTTPONLY", True)
COOKIE_PATH = getattr(settings, "COOKIE_PATH", "/")
COOKIE_DOMAIN = getattr(settings, "COOKIE_DOMAIN", None)  # 필요시 settings에 추가

_simple_jwt = getattr(settings, "SIMPLE_JWT", {})
_access_lifetime = _simple_jwt.get("ACCESS_TOKEN_LIFETIME")
_refresh_lifetime = _simple_jwt.get("REFRESH_TOKEN_LIFETIME")

def _lifetime_seconds(td):
    if isinstance(td, timedelta):
        return int(td.total_seconds())
    return None

ACCESS_COOKIE_MAX_AGE = _lifetime_seconds(_access_lifetime)
REFRESH_COOKIE_MAX_AGE = _lifetime_seconds(_refresh_lifetime)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):

        refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if refresh_token:

            mutable_data = request.data.copy()
            mutable_data["refresh"] = refresh_token
            request._full_data = mutable_data  # DRF 내부에서 읽을 때 사용되기도 함
            request.data = mutable_data

        super_response = super().post(request, *args, **kwargs)

        if super_response.status_code != status.HTTP_200_OK:

            return super_response

        access = super_response.data.get("access")
        refresh = super_response.data.get("refresh")


        final_response = Response({"access": access}, status=super_response.status_code)


        if access is not None:
            final_response.set_cookie(
                ACCESS_COOKIE_NAME,
                access,
                max_age=ACCESS_COOKIE_MAX_AGE,
                secure=COOKIE_SECURE,
                httponly=COOKIE_HTTPONLY,
                samesite=COOKIE_SAMESITE,
                path=COOKIE_PATH,
                domain=COOKIE_DOMAIN,
            )


        if refresh is not None:
            final_response.set_cookie(
                REFRESH_COOKIE_NAME,
                refresh,
                max_age=REFRESH_COOKIE_MAX_AGE,
                secure=COOKIE_SECURE,
                httponly=COOKIE_HTTPONLY,
                samesite=COOKIE_SAMESITE,
                path=COOKIE_PATH,
                domain=COOKIE_DOMAIN,
            )

        return final_response
