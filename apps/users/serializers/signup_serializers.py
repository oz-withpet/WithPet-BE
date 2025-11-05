from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users.models import CustomUser
from users.models.email_verification import EmailVerification  # 이메일 인증 코드 모델 (별도 설명 아래)


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    verification_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'name',
            'nickname',
            'pet_type',
            'gender',
            'password',
            'password_confirm',
            'verification_code',
        ]

    def validate_nickname(self, value):
        if CustomUser.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})

        # 이메일 인증 코드 검증
        try:
            email_record = EmailVerification.objects.get(email=data['email'])
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError({"email": "인증 코드가 존재하지 않습니다."})

        if email_record.code != data['verification_code']:
            raise serializers.ValidationError({"verification_code": "인증 코드가 올바르지 않습니다."})

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data.pop('verification_code')
        user = CustomUser.objects.create_user(**validated_data)
        return user
