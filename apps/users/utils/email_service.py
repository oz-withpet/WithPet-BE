import random
from django.core.mail import send_mail
from django.core.cache import cache

def send_verification_email(email):
    code = str(random.randint(100000, 999999))
    cache.set(email, code, timeout=300)  # 5분간 유효
    send_mail(
        'WithPet 회원가입 인증코드',
        f'인증코드는 {code} 입니다. 5분 내에 입력해주세요.',
        'no-reply@withpet.com',
        [email],
        fail_silently=False,
    )
