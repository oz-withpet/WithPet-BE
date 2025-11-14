from rest_framework import serializers
from ..models import Store


class StoreSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    name = serializers.CharField(source='store_name', read_only=True)

    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'category',
            'address',
            'phone',
            'tags',
            'operating_information',
            'kakao_place_id',
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
            'full_address': obj.road_address or f"{obj.province} {obj.district} {obj.neighborhood} {obj.detail_address}",
            'latitude': float(obj.latitude),
            'longitude': float(obj.longitude),
        }


class StoreListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='store_name')
    category_name = serializers.CharField()

    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'category_name',
            'province',
            'district',
            'phone',
            'latitude',
            'longitude'
        ]