from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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
    gender = models.CharField(max_length=10, choices=[("male", "남자"), ("female", "여자")])
    pet_type = models.CharField(max_length=10, choices=[("dog", "강아지"), ("cat", "고양이")])

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname", "gender", "pet_type"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
