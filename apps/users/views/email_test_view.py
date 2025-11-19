from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

def test_email(request):
    send_mail(
        subject="테스트 이메일",
        message="이건 SES SMTP 테스트입니다.",
        from_email=settings.DEFAULT_FROM_EMAIL,   # Gmail 주소 사용
        recipient_list=["jisun131200@gmail.com"],
        fail_silently=False,
    )
    return JsonResponse({"message": "테스트 이메일 발송 완료!"})

