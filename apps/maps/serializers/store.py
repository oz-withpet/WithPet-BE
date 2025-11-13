from rest_framework import serializers
from ..models import Store


class StoreSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    name = serializers.CharField(source='store_name')

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'category', 'address', 'phone',
            'tags', 'operating_information',
            'kakao_place_id'
        ]

    def get_category(self, obj):
        return {
            'code': obj.category_code,
            'name': obj.category_name
        }

    def get_address(self, obj):
        return {
            'province': obj.province,
            'district': obj.district,
            'neighborhood': obj.neighborhood,
            'detail': obj.detail_address,
            'full_address': obj.road_address or obj.full_address_property,
            'latitude': float(obj.latitude),
            'longtitude': float(obj.longitude),
        }