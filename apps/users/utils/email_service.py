import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def send_verification_email(email):
    email = email.lower()

    code = str(random.randint(100000, 999999))
    cache_key = f"email_code:{email}"

    cache.set(cache_key, code, timeout=300)

    subject = "WithPet 회원가입 인증코드"
    message = f"인증코드는 {code} 입니다.\n5분 내에 입력해주세요."

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def verify_email_code(email, code):
    email = email.lower()

    cache_key = f"email_code:{email}"
    cached_code = cache.get(cache_key)

    if cached_code is None:
        return False

    if str(cached_code) != str(code):
        return False

    cache.delete(cache_key)

    return True
