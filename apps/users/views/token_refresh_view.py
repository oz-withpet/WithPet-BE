from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer
