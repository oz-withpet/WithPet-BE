from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'nickname',
            'email',
            'password',
            'pet_type',
            'gender',
        ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

