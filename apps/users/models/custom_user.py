from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수 입력 항목입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    PET_CHOICES = (
        ('dog', '강아지'),
        ('cat', '고양이'),
    )
    GENDER_CHOICES = (
        ('male', '남자'),
        ('female', '여자'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=30, unique=True)
    pet_type = models.CharField(max_length=10, choices=PET_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'name', 'pet_type', 'gender']

    def __str__(self):
        return self.email
