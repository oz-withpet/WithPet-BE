from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.users.serializers.signup_serializer import SignupSerializer
from apps.users.utils.email_service import send_verification_email
from apps.users.models import CustomUser
from django.core.cache import cache
from drf_spectacular.utils import extend_schema


class SendVerificationCodeView(APIView):
    """
    1️⃣ 이메일로 인증코드를 발송하는 API
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={"application/json": {"email": "string"}},
        responses={200: {"detail": "인증코드가 이메일로 발송되었습니다."}},
        description="이메일을 입력하면 인증코드를 전송합니다."
    )

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': '이메일을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        send_verification_email(email)
        return Response({'detail': '인증코드가 이메일로 발송되었습니다.'}, status=status.HTTP_200_OK)


class VerifyNicknameView(APIView):
    """
    2️⃣ 닉네임 중복 확인
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={"application/json": {"nickname": "string"}},
        responses={200: {"detail": "사용 가능한 닉네임입니다."}},
        description="닉네임 중복 여부를 확인합니다."
    )

    def post(self, request):
        nickname = request.data.get('nickname')
        if not nickname:
            return Response({'detail': '닉네임을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(nickname=nickname).exists():
            return Response({'detail': '이미 사용 중인 닉네임입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': '사용 가능한 닉네임입니다.'}, status=status.HTTP_200_OK)


class SignupAPIView(APIView):
    """
    3️⃣ 인증코드 확인 후 회원가입 완료
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=SignupSerializer,
        responses={201: SignupSerializer},
        description="이메일과 인증코드를 검증하고 회원가입을 완료합니다."
    )

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'detail': '이메일과 인증코드를 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        cached_code = cache.get(email)
        if cached_code != code:
            return Response({'detail': '인증코드가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(email)
            return Response({'detail': '회원가입이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
