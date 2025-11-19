from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.users.models import CustomUser
from ..utils.profanity_filter import contains_profanity


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    # code = serializers.CharField(write_only=True)  # 인증 코드 필드 추가

    class Meta:
        model = CustomUser
        fields = ['email', 'nickname', 'password', 'password2', 'pet_type', 'gender']

    def validate_nickname(self, value):
        if contains_profanity(value):
            raise serializers.ValidationError("닉네임에 비속어 또는 부적절한 단어가 포함되어 있습니다.")
        return value

    def validate_email(self, value):
        if contains_profanity(value):
            raise serializers.ValidationError("이메일에 부적절한 단어가 포함되어 있습니다.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': '비밀번호가 일치하지 않습니다.'})

        # # 인증 코드 검증
        # email = attrs.get('email')
        # code = attrs.get('code')
        # if not verify_email_code(email, code):
        #     raise serializers.ValidationError({'code': '인증 코드가 일치하지 않습니다.'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        # validated_data.pop('code')  # code는 DB에 저장할 필요 없음
        user = CustomUser.objects.create_user(**validated_data)
        return user
