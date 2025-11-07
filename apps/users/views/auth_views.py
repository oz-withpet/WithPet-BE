from rest_framework import generics, permissions
from users.serializers.user_serializers import UserSerializer
from users.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
