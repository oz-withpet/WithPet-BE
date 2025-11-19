from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        data = response.data
        access_token = data.get("access")
        refresh_token = data.get("refresh")

        # 반환할 Body는 access만 남기기
        response.data = {
            "access": access_token
        }

        # Access Token 쿠키 설정 제거 ( 프론트엔드 메모리로 유도 )
        # if access_token:
        #     response.set_cookie(
        #         key="access_token",
        #         value=access_token,
        #         httponly=True,
        #         secure=True,
        #         samesite="None",
        #         max_age=60 * 60,
        #     )

        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=60 * 60 * 24 * 14,
            )

        return response

