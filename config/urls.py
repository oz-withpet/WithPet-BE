from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include

urlpatterns = [
    # --- 1. 관리자, 문서, 토큰 ---
    path("admin/", admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- 2. Community, Users ---
    path('', include('apps.users.urls')),
    path("", include("apps.community.posts.urls")),
    path("", include("apps.community.comments.urls")),
    path("", include("apps.community.likes.urls")),
    path("", include("apps.community.reports.urls")),

    # --- 3. Mypage ---
    path('mypage/', include('apps.mypage.urls')),

    # --- 4. Maps ---
    path('', include('apps.maps.urls')),
]

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns += [
    path('sentry-debug/', trigger_error),
    # ...
]
