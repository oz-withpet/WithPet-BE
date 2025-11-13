# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from apps.users.models import CustomUser

class EmailCheckAPIView(APIView):
    @extend_schema(
        summary="이메일 중복 확인",
        description="입력한 이메일이 이미 가입된 사용자인지 확인합니다.",
        parameters=[
            OpenApiParameter(
                name="email",
                description="중복 확인할 이메일 주소",
                required=True,
                type=str,
            ),
        ],
        examples=[
            OpenApiExample(
                name="성공 예시",
                value={"available": True, "message": "사용 가능한 이메일입니다."},
            ),
            OpenApiExample(
                name="중복 예시",
                value={"available": False, "message": "이미 사용 중인 이메일입니다."},
            ),
        ],
        responses={200: None, 400: None},
    )
    def get(self, request):
        email = request.GET.get("email")
        if not email:
            return Response({"error": "이메일이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        exists = CustomUser.objects.filter(email=email).exists()
        if exists:
            return Response({"available": False, "message": "이미 사용 중인 이메일입니다."})
        return Response({"available": True, "message": "사용 가능한 이메일입니다."})
