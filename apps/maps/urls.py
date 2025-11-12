from django.urls import path
from apps.maps.views import StoreListAPIView, StoreDetailAPIView

app_name = 'maps'

urlpatterns = [
    # 매장 목록
    path('stores/', StoreListAPIView.as_view(), name='store-list'),

    # 가게 상세
    path('stores/<int:pk>/', StoreDetailAPIView.as_view(), name='store-detail'),

    # 나중에 추가할 API들
    # path('stores/nearby/', StoreNearbyAPIView.as_view(), name='store-nearby'),
    # path('markers/', MapMarkersAPIView.as_view(), name='map-markers'),
]