from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StoreViewSet,
    LikeViewSet,
    ProvinceListAPIView,
    DistrictListAPIView,
    LocationProvinceAPIView,
    LocationDistrictAPIView,
    LocationNeighborhoodAPIView,
)

router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'likes', LikeViewSet, basename='like')

app_name = 'maps'

urlpatterns = [
    path('', include(router.urls)),

    path('provinces/', ProvinceListAPIView.as_view(), name='province-list'),
    path('provinces/<str:province_name>/districts/', DistrictListAPIView.as_view(), name='district-list'),

    path('locations/', LocationProvinceAPIView.as_view(), name='location-provinces'),
    path('locations/<int:province_code>/', LocationDistrictAPIView.as_view(), name='location-districts'),
    path('locations/<int:province_code>/<int:district_code>/', LocationNeighborhoodAPIView.as_view(),
         name='location-neighborhoods'),

    path('categories/', StoreViewSet.as_view({'get': 'categories'}), name='categories-legacy'),
]