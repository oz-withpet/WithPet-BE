from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from .enums import GenderEnum, PetTypeEnum


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=20, unique=True)

    gender = models.CharField(
        max_length=10,
        choices=[(tag.value, tag.name.capitalize()) for tag in GenderEnum],
    )

    pet_type = models.CharField(
        max_length=10,
        choices=[(tag.value, tag.name.capitalize()) for tag in PetTypeEnum],
    )

    # --------------------------------
    # 이메일 인증 미사용으로 인한 조치 시작 (default=False) -> (default=True)
    # --------------------------------

    is_email_verified = models.BooleanField(default=True)

    # --------------------------------
    # 이메일 인증 미사용으로 인한 조치 끝
    # --------------------------------

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname", "gender", "pet_type"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
