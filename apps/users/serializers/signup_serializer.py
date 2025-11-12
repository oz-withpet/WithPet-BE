from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.users.models import CustomUser


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)  # 비밀번호 재입력 확인용

    class Meta:
        model = CustomUser
        fields = ['email', 'nickname', 'password', 'password2', 'pet_type', 'gender']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': '비밀번호가 일치하지 않습니다.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user
