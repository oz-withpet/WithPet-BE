# ⚙️ 자동 변환됨: drf_yasg → drf_spectacular
# ✅ 필요 시 Serializer를 명시해 request/response를 세부적으로 조정하세요.

# apps/users/views/email_check_view.py
from rest_framework import generics, serializers, permissions, status
from rest_framework.response import Response
from apps.users.models import CustomUser


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailCheckAPIView(generics.GenericAPIView):
    """
    이메일 중복 확인 API
    - 이미 가입된 이메일인지 검사
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailCheckSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        if CustomUser.objects.filter(email=email).exists():
            return Response({'detail': '이미 가입된 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': '사용 가능한 이메일입니다.'}, status=status.HTTP_200_OK)
