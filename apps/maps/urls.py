from django.urls import path
from .views import (
    StoreListAPIView,
    StoreDetailAPIView,
    StoreSearchAPIView,
    ProvinceListAPIView,
    DistrictListAPIView,
    UserLikePlaceListAPIView,
    UserLikePlaceDetailAPIView,
)

app_name = 'maps'

urlpatterns = [
    path('stores/', StoreListAPIView.as_view(), name='store-list'),
    path('stores/search/', StoreSearchAPIView.as_view(), name='store-search'),
    path('stores/<int:store_id>/', StoreDetailAPIView.as_view(), name='store-detail'),
    path('map/provinces/', ProvinceListAPIView.as_view(), name='province-list'),
    path('map/provinces/<str:province>/districts/', DistrictListAPIView.as_view(), name='district-list'),
    path('users/<int:user_id>/like_places/', UserLikePlaceListAPIView.as_view(), name='user-likes'),
    path('users/<int:user_id>/like_places/<int:like_id>/', UserLikePlaceDetailAPIView.as_view(),
         name='user-like-detail'),
]