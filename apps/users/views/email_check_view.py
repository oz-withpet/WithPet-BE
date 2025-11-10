from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.users.models import CustomUser

class EmailCheckAPIView(APIView):
    """
    이메일 중복 확인 API
    - 이미 가입된 이메일인지 검사
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'detail': '이메일을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({'detail': '이미 가입된 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)
