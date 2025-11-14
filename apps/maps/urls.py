from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StoreViewSet,
    LikeViewSet,
    ProvinceListAPIView,
    DistrictListAPIView,
)

router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'likes', LikeViewSet, basename='like')

app_name = 'maps'

urlpatterns = [
    path('', include(router.urls)),
    path('provinces/', ProvinceListAPIView.as_view(), name='province-list'),
    path('provinces/<str:province_name>/districts/', DistrictListAPIView.as_view(), name='district-list'),
]