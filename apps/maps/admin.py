from django.contrib import admin
from .models import Store, LikePlace


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'store_name', 'category_name', 'province',
        'district', 'phone', 'is_active'
    ]
    list_filter = ['category_name', 'province', 'district', 'is_active']
    search_fields = ['store_name', 'road_address', 'phone']
    readonly_fields = [
        'kakao_place_id', 'latitude', 'longitude',
        'created_at', 'updated_at', 'last_seen_at'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('store_name', 'category_name', 'category_code', 'phone')
        }),
        ('주소 정보', {
            'fields': (
                'province', 'district', 'neighborhood',
                'detail_address', 'road_address'
            )
        }),
        ('위치 정보', {
            'fields': ('latitude', 'longitude', 'kakao_place_id')
        }),
        ('추가 정보', {
            'fields': (
                'tags', 'operating_information',
                'rating', 'review_count', 'like_count'
            )
        }),
        ('상태', {
            'fields': ('is_active', 'created_at', 'updated_at', 'last_seen_at')
        }),
    )


@admin.register(LikePlace)
class LikePlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'store', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'store__store_name']
    raw_id_fields = ['user', 'store']