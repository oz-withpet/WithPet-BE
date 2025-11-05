import random
from django.core.mail import send_mail
from users.models.email_verification import EmailVerification

def send_verification_email(email):
    code = str(random.randint(100000, 999999))
    EmailVerification.objects.update_or_create(email=email, defaults={'code': code})
    send_mail(
        subject='WithPet 이메일 인증 코드',
        message=f'인증코드: {code}\n5분 안에 입력해주세요.',
        from_email='no-reply@withpet.com',
        recipient_list=[email],
    )
    return code
