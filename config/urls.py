from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('apps.users.urls')),
    path("", include("apps.community.posts.urls")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),                      # OpenAPI JSON/YAML
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),# 내장 Swagger UI
    path("", include("apps.community.posts.urls")),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("", include("apps.community.comments.urls")),
    path("", include("apps.community.likes.urls")),
    path("", include("apps.community.reports.urls")),
    path('', include('apps.maps.urls')),
    path('mypage/', include('apps.mypage.urls'))
]


def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns += [
    path('sentry-debug/', trigger_error),
    # ...
]
