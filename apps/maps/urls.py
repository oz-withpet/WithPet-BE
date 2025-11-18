from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StoreListAPIView,
    StoreDetailAPIView,
    CategoryListAPIView,
    LikeViewSet,
    ProvinceListAPIView,
    DistrictListAPIView,
    LocationProvinceAPIView,
    LocationDistrictAPIView,
    LocationNeighborhoodAPIView,
)

# ViewSet은 router 사용
router = DefaultRouter()
router.register(r'likes', LikeViewSet, basename='like')

app_name = 'maps'

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),

    path('stores/', StoreListAPIView.as_view(), name='store-list'),
    path('stores/<int:pk>/', StoreDetailAPIView.as_view(), name='store-detail'),

    path('categories/', CategoryListAPIView.as_view(), name='category-list'),

    path('provinces/', ProvinceListAPIView.as_view(), name='province-list'),
    path('provinces/<str:province_name>/districts/', DistrictListAPIView.as_view(), name='district-list'),

    path('locations/', LocationProvinceAPIView.as_view(), name='location-provinces'),
    path('locations/<int:province_code>/', LocationDistrictAPIView.as_view(), name='location-districts'),
    path('locations/<int:province_code>/<int:district_code>/', LocationNeighborhoodAPIView.as_view(),
         name='location-neighborhoods'),
]